import asyncio
from concurrent.futures import ThreadPoolExecutor
from flask import jsonify
import logging
from src.search.model import gemini_model, clip_embedding, bgem3_embedding, bm25_embedding
from src.search.qdrant_db import image_qdrant_client_1, image_qdrant_client_2, content_qdrant_client,caption_qdrant_client
from src.search.search_method import image_search_1, image_search_2, content_search,caption_search
from src.rerank.rerank import rerank_images
from src.utils import deduplicate_and_sort,normalize_scores

logger = logging.getLogger(__name__)
CLOUDFRONT_BASE = "https://d1zgby2rss028i.cloudfront.net"

class BaseSearchService:
    """Base class cho các search service"""
    def __init__(self, max_workers=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def __del__(self):
        """Cleanup khi object bị destroy"""
        self.executor.shutdown(wait=True)
    
    def shutdown(self):
        """Explicit method để shutdown executor"""
        self.executor.shutdown(wait=True)

    async def _generate_query_with_gemini(self, query, loop):
        """Generate query với gemini"""
        try:
            eng_query = await loop.run_in_executor(
                self.executor,
                gemini_model.generate_content, 
                query
            )
            logger.info(f"Rewritten Query: {eng_query}")
            return eng_query
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return query  # Fallback về query gốc

    async def _get_content_results(self, flagValue, loop):
        """Lấy content results nếu có flagValue"""
        if not flagValue:
            return []
        
        try:
            content_results = await loop.run_in_executor(
                self.executor, 
                content_search, 
                flagValue, 
                bgem3_embedding, 
                bm25_embedding, 
                content_qdrant_client
            )
            return content_results if not isinstance(content_results, Exception) else []
        except Exception as e:
            logger.error(f"Content search error: {e}")
            return []


class ImageSearchService(BaseSearchService):
    """Service chuyên cho image search"""
    
    async def process_with_executor(self, request):
        """Main method để xử lý image search request"""
        try:
            data = request.get_json()
            query = data.get("query", "")
            flagValue = data.get("flagValue", "")
            
            if not query:
                return jsonify({"error": "Query is required"}), 400
            
            loop = asyncio.get_event_loop()
            
            if flagValue:
                return await self._process_with_flag(query, flagValue, loop)
            else:
                return await self._process_without_flag(query, loop)
                
        except Exception as e:
            logger.error(f"Error in ImageSearchService.process_with_executor: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    async def _process_with_flag(self, query, flagValue, loop):
        """Xử lý image search khi có flagValue"""
        try:
            # Bước 1: Chạy gemini và content search song song
            gemini_future = self._generate_query_with_gemini(query, loop)
            content_future = self._get_content_results(flagValue, loop)
            
            eng_query, content_results = await asyncio.gather(
                gemini_future, 
                content_future,
                return_exceptions=True
            )
            
            # Xử lý lỗi
            if isinstance(eng_query, Exception):
                eng_query = query
            if isinstance(content_results, Exception):
                content_results = []
            
            # Bước 2: Tìm kiếm ảnh từ 2 client song song
            image_results_1, image_results_2 = await self._search_images_parallel(eng_query, loop)
            
            # Bước 3: Normalize và combine results
            image_results_1 = normalize_scores(image_results_1)
            image_results_2 = normalize_scores(image_results_2)
            image_results = image_results_1 + image_results_2
            
            # Bước 4: Rerank hoặc deduplicate
            final_results = await self._process_final_results(
                image_results, content_results, loop
            )
            
            return jsonify({"images": final_results[:300]})
            
        except Exception as e:
            logger.error(f"Error in ImageSearchService._process_with_flag: {str(e)}")
            return await self._process_without_flag(query, loop)

    async def _process_without_flag(self, query, loop):
        """Xử lý image search khi không có flagValue"""
        try:
            # Bước 1: Generate query với gemini
            eng_query = await self._generate_query_with_gemini(query, loop)
            
            # Bước 2: Tìm kiếm ảnh từ 2 client song song
            image_results_1, image_results_2 = await self._search_images_parallel(eng_query, loop)
            
            # Bước 3: Normalize và combine
            image_results_1 = normalize_scores(image_results_1)
            image_results_2 = normalize_scores(image_results_2)
            retrieve_results = image_results_1 + image_results_2
            
            # Bước 4: Deduplicate
            final_results = await self._deduplicate_results(retrieve_results, loop)
            
            return jsonify({"images": final_results[:200]})
            
        except Exception as e:
            logger.error(f"Error in ImageSearchService._process_without_flag: {str(e)}")
            return jsonify({"images": []}), 500

    async def _search_images_parallel(self, eng_query, loop):
        """Tìm kiếm ảnh từ 2 client song song"""
        img1_future = loop.run_in_executor(
            self.executor,
            image_search_1, 
            eng_query, 
            clip_embedding, 
            image_qdrant_client_1
        )
        img2_future = loop.run_in_executor(
            self.executor,
            image_search_2, 
            eng_query, 
            clip_embedding, 
            image_qdrant_client_2
        )
        
        image_results_1, image_results_2 = await asyncio.gather(
            img1_future, 
            img2_future,
            return_exceptions=True
        )
        
        # Xử lý lỗi
        if isinstance(image_results_1, Exception):
            logger.error(f"Image search 1 error: {image_results_1}")
            image_results_1 = []
            
        if isinstance(image_results_2, Exception):
            logger.error(f"Image search 2 error: {image_results_2}")
            image_results_2 = []
        
        return image_results_1, image_results_2

    async def _process_final_results(self, image_results, content_results, loop):
        """Xử lý kết quả cuối cùng với rerank hoặc deduplicate"""
        if image_results and content_results:
            # Có cả image và content results -> rerank
            reranked_results = await loop.run_in_executor(
                self.executor,
                rerank_images, 
                image_results, 
                content_results
            )
            return [f"{CLOUDFRONT_BASE}/{res['path']}" for res in reranked_results]
        else:
            # Không có content -> chỉ deduplicate
            return await self._deduplicate_results(image_results, loop)

    async def _deduplicate_results(self, results, loop):
        """Deduplicate và format results"""
        if results:
            deduplicated_results = await loop.run_in_executor(
                self.executor,
                deduplicate_and_sort,
                results
            )
            return [f"{CLOUDFRONT_BASE}/{res['path']}" for res in deduplicated_results]
        else:
            return []


class CaptionSearchService(BaseSearchService):
    """Service chuyên cho caption search"""
    
    async def process_with_executor(self, request):
        """Main method để xử lý caption search request"""
        try:
            data = request.get_json()
            query = data.get("query", "")
            flagValue = data.get("flagValue", "")
            
            if not query:
                return jsonify({"error": "Query is required"}), 400
            
            loop = asyncio.get_event_loop()
            
            if flagValue:
                return await self._process_with_flag(query, flagValue, loop)
            else:
                return await self._process_without_flag(query, loop)
                
        except Exception as e:
            logger.error(f"Error in CaptionSearchService.process_with_executor: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    async def _process_with_flag(self, query, flagValue, loop):
        """Xử lý caption search khi có flagValue"""
        try:
            # Bước 1: Chạy gemini và content search song song
            gemini_future = self._generate_query_with_gemini(query, loop)
            content_future = self._get_content_results(flagValue, loop)
            
            eng_query, content_results = await asyncio.gather(
                gemini_future, 
                content_future,
                return_exceptions=True
            )
            
            # Xử lý lỗi
            if isinstance(eng_query, Exception):
                eng_query = query
            if isinstance(content_results, Exception):
                content_results = []
            
            # Bước 2: Tìm kiếm caption
            caption_results = await self._search_captions(eng_query, loop)
            
            # Bước 3: Normalize
            caption_results = normalize_scores(caption_results)
            
            # Bước 4: Rerank hoặc deduplicate
            final_results = await self._process_final_results(
                caption_results, content_results, loop
            )
            
            return jsonify({"images": final_results[:300]})
            
        except Exception as e:
            logger.error(f"Error in CaptionSearchService._process_with_flag: {str(e)}")
            return await self._process_without_flag(query, loop)

    async def _process_without_flag(self, query, loop):
        """Xử lý caption search khi không có flagValue"""
        try:
            # Bước 1: Generate query với gemini
            eng_query = await self._generate_query_with_gemini(query, loop)
            
            # Bước 2: Tìm kiếm caption
            caption_results = await self._search_captions(eng_query, loop)
            
            # Bước 3: Normalize
            caption_results = normalize_scores(caption_results)
            print("caption", caption_results)
            
            # Bước 4: Deduplicate
            final_results = await self._deduplicate_results(caption_results, loop)
            
            return jsonify({"images": final_results[:200]})
            
        except Exception as e:
            logger.error(f"Error in CaptionSearchService._process_without_flag: {str(e)}")
            return jsonify({"images": []}), 500

    async def _search_captions(self, eng_query, loop):
        """Tìm kiếm caption"""
        try:
            caption_results = await loop.run_in_executor(
                self.executor,
                caption_search, 
                eng_query, 
                bgem3_embedding, 
                bm25_embedding, 
                caption_qdrant_client
            )
            
            if isinstance(caption_results, Exception):
                logger.error(f"Caption search error: {caption_results}")
                return []
            
            return caption_results
            
        except Exception as e:
            logger.error(f"Error in _search_captions: {e}")
            return []

    async def _process_final_results(self, caption_results, content_results, loop):
        """Xử lý kết quả cuối cùng với rerank hoặc deduplicate"""
        if caption_results and content_results:
            # Có cả caption và content results -> rerank
            reranked_results = await loop.run_in_executor(
                self.executor,
                rerank_images, 
                caption_results, 
                content_results
            )
            return [f"{CLOUDFRONT_BASE}/{res['path']}" for res in reranked_results]
        else:
            # Không có content -> chỉ deduplicate
            return await self._deduplicate_results(caption_results, loop)

    async def _deduplicate_results(self, results, loop):
        """Deduplicate và format results"""
        if results:
            deduplicated_results = await loop.run_in_executor(
                self.executor,
                deduplicate_and_sort,
                results
            )
            return [f"{CLOUDFRONT_BASE}/{res['path']}" for res in deduplicated_results]
        else:
            return []


class CombinedSearchService(BaseSearchService):
    """Service kết hợp cả image và caption search (giống như code gốc)"""
    
    async def process_with_executor(self, request):
        """Main method để xử lý combined search request"""
        try:
            data = request.get_json()
            query = data.get("query", "")
            flagValue = data.get("flagValue", "")
            
            if not query:
                return jsonify({"error": "Query is required"}), 400
            
            loop = asyncio.get_event_loop()
            
            if flagValue:
                return await self._process_with_flag(query, flagValue, loop)
            else:
                return await self._process_without_flag(query, loop)
                
        except Exception as e:
            logger.error(f"Error in CombinedSearchService.process_with_executor: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    async def _process_with_flag(self, query, flagValue, loop):
        """Xử lý combined search khi có flagValue"""
        try:
            # Bước 1: Chạy gemini và content search song song
            gemini_future = self._generate_query_with_gemini(query, loop)
            content_future = self._get_content_results(flagValue, loop)
            
            eng_query, content_results = await asyncio.gather(
                gemini_future, 
                content_future,
                return_exceptions=True
            )
            
            # Xử lý lỗi
            if isinstance(eng_query, Exception):
                eng_query = query
            if isinstance(content_results, Exception):
                content_results = []
            
            # Bước 2: Tìm kiếm ảnh và caption song song
            img1_future = loop.run_in_executor(
                self.executor,
                image_search_1, 
                eng_query, 
                clip_embedding, 
                image_qdrant_client_1
            )
            img2_future = loop.run_in_executor(
                self.executor,
                image_search_2, 
                eng_query, 
                clip_embedding, 
                image_qdrant_client_2
            )
            caption_future = loop.run_in_executor(
                self.executor,
                caption_search, 
                eng_query, 
                bgem3_embedding, 
                bm25_embedding, 
                caption_qdrant_client
            )
            
            image_results_1, image_results_2, caption_results = await asyncio.gather(
                img1_future, 
                img2_future,
                caption_future,
                return_exceptions=True
            )
            
            # Xử lý lỗi từ search
            if isinstance(image_results_1, Exception):
                logger.error(f"Image search 1 error: {image_results_1}")
                image_results_1 = []
                
            if isinstance(image_results_2, Exception):
                logger.error(f"Image search 2 error: {image_results_2}")
                image_results_2 = []
            
            if isinstance(caption_results, Exception):
                logger.error(f"Caption search error: {caption_results}")
                caption_results = []

            # Bước 3: Normalize và combine
            caption_results = normalize_scores(caption_results)
            image_results_1 = normalize_scores(image_results_1)
            image_results_2 = normalize_scores(image_results_2)
            image_results = image_results_1 + image_results_2 + caption_results
            
            # Bước 4: Rerank hoặc deduplicate
            final_results = await self._process_final_results(
                image_results, content_results, loop
            )
            
            return jsonify({"images": final_results[:300]})
            
        except Exception as e:
            logger.error(f"Error in CombinedSearchService._process_with_flag: {str(e)}")
            return await self._process_without_flag(query, loop)

    async def _process_without_flag(self, query, loop):
        """Xử lý combined search khi không có flagValue"""
        try:
            # Bước 1: Generate query với gemini
            eng_query = await self._generate_query_with_gemini(query, loop)
            
            # Bước 2: Tìm kiếm ảnh và caption song song
            img1_future = loop.run_in_executor(
                self.executor,
                image_search_1, 
                eng_query, 
                clip_embedding, 
                image_qdrant_client_1
            )
            img2_future = loop.run_in_executor(
                self.executor,
                image_search_2, 
                eng_query, 
                clip_embedding, 
                image_qdrant_client_2
            )
            caption_future = loop.run_in_executor(
                self.executor,
                caption_search, 
                eng_query, 
                bgem3_embedding, 
                bm25_embedding, 
                caption_qdrant_client
            )
            
            image_results_1, image_results_2, caption_results = await asyncio.gather(
                img1_future, 
                img2_future,
                caption_future,
                return_exceptions=True
            )
            
            # Xử lý lỗi từ search
            if isinstance(image_results_1, Exception):
                logger.error(f"Image search 1 error: {image_results_1}")
                image_results_1 = []
                
            if isinstance(image_results_2, Exception):
                logger.error(f"Image search 2 error: {image_results_2}")
                image_results_2 = []

            if isinstance(caption_results, Exception):
                logger.error(f"Caption search error: {caption_results}")
                caption_results = []

            # Bước 3: Normalize và combine
            caption_results = normalize_scores(caption_results)
            image_results_1 = normalize_scores(image_results_1)
            image_results_2 = normalize_scores(image_results_2)
            retrieve_results = image_results_1 + image_results_2 + caption_results
            
            print("caption", caption_results)
            print("image", image_results_1)
            
            # Bước 4: Deduplicate
            final_results = await self._deduplicate_results(retrieve_results, loop)
            
            return jsonify({"images": final_results[:200]})
            
        except Exception as e:
            logger.error(f"Error in CombinedSearchService._process_without_flag: {str(e)}")
            return jsonify({"images": []}), 500

    async def _process_final_results(self, image_results, content_results, loop):
        """Xử lý kết quả cuối cùng với rerank hoặc deduplicate"""
        if image_results and content_results:
            # Có cả image và content results -> rerank
            reranked_results = await loop.run_in_executor(
                self.executor,
                rerank_images, 
                image_results, 
                content_results
            )
            return [f"{CLOUDFRONT_BASE}/{res['path']}" for res in reranked_results]
        else:
            # Không có content -> chỉ deduplicate
            return await self._deduplicate_results(image_results, loop)

    async def _deduplicate_results(self, results, loop):
        """Deduplicate và format results"""
        if results:
            deduplicated_results = await loop.run_in_executor(
                self.executor,
                deduplicate_and_sort,
                results
            )
            return [f"{CLOUDFRONT_BASE}/{res['path']}" for res in deduplicated_results]
        else:
            return []

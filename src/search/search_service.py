import asyncio
from concurrent.futures import ThreadPoolExecutor
from flask import jsonify
import logging
from src.search.model import gemini_model, clip_embedding, bgem3_embedding, bm25_embedding
from src.search.qdrant_db import image_qdrant_client_1, image_qdrant_client_2, content_qdrant_client
from src.search.search_method import image_search_1, image_search_2, content_search
from src.rerank.rerank import rerank_images
from src.utils import deduplicate_and_sort

logger = logging.getLogger(__name__)
CLOUDFRONT_BASE = "https://d1zgby2rss028i.cloudfront.net"

class SearchService:
    def __init__(self, max_workers=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_with_executor(self, request):
        """
        Sử dụng ThreadPoolExecutor để kiểm soát số lượng thread
        """
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
            logger.error(f"Error in process_with_executor: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    async def _process_with_flag(self, query, flagValue, loop):
        """
        Xử lý khi có flagValue
        """
        try:
            # Bước 1: Chạy gemini và content search song song
            gemini_future = loop.run_in_executor(
                self.executor, 
                gemini_model.generate_content, 
                query
            )
            content_future = loop.run_in_executor(
                self.executor, 
                content_search, 
                flagValue, 
                bgem3_embedding, 
                bm25_embedding, 
                content_qdrant_client
            )
            
            eng_query, content_results = await asyncio.gather(
                gemini_future, 
                content_future,
                return_exceptions=True
            )
            
            # Xử lý lỗi từ gemini
            if isinstance(eng_query, Exception):
                logger.error(f"Gemini error: {eng_query}")
                eng_query = query  # Fallback về query gốc
            
            # Xử lý lỗi từ content search
            if isinstance(content_results, Exception):
                logger.error(f"Content search error: {content_results}")
                content_results = []  # Fallback về list rỗng
            
            logger.info(f"Rewritten Query: {eng_query}")
            
            # Bước 2: Tìm kiếm ảnh song song
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
            
            # Xử lý lỗi từ image search
            if isinstance(image_results_1, Exception):
                logger.error(f"Image search 1 error: {image_results_1}")
                image_results_1 = []
                
            if isinstance(image_results_2, Exception):
                logger.error(f"Image search 2 error: {image_results_2}")
                image_results_2 = []
            
            # Bước 3: Kết hợp và rerank
            image_results = image_results_1 + image_results_2
            
            if image_results and content_results:
                # Có cả image và content results -> rerank
                reranked_results = await loop.run_in_executor(
                    self.executor,
                    rerank_images, 
                    image_results, 
                    content_results
                )
                final_results = [f"{CLOUDFRONT_BASE}/{res['path']}" for res in reranked_results]
            else:
                # Không có content hoặc không có image -> chỉ deduplicate
                if image_results:
                    deduplicated_results = await loop.run_in_executor(
                        self.executor,
                        deduplicate_and_sort,
                        image_results
                    )
                    final_results = [f"{CLOUDFRONT_BASE}/{res['path']}" for res in deduplicated_results]
                else:
                    final_results = []
            
            return jsonify({"images": final_results[:200]})
            
        except Exception as e:
            logger.error(f"Error in _process_with_flag: {str(e)}")
            # Fallback: thử xử lý như không có flag
            return await self._process_without_flag(query, loop)
    
    async def _process_without_flag(self, query, loop):
        """
        Xử lý khi không có flagValue - chỉ tìm ảnh
        """
        try:
            # Bước 1: Generate query với gemini
            eng_query = await loop.run_in_executor(
                self.executor,
                gemini_model.generate_content, 
                query
            )
            
            logger.info(f"Rewritten Query: {eng_query}")
            
            # Bước 2: Tìm kiếm ảnh từ 2 client song song
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
            
            # Xử lý lỗi từ image search
            if isinstance(image_results_1, Exception):
                logger.error(f"Image search 1 error: {image_results_1}")
                image_results_1 = []
                
            if isinstance(image_results_2, Exception):
                logger.error(f"Image search 2 error: {image_results_2}")
                image_results_2 = []
            
            # Bước 3: Kết hợp và deduplicate
            image_results = image_results_1 + image_results_2
            
            if image_results:
                deduplicated_results = await loop.run_in_executor(
                    self.executor,
                    deduplicate_and_sort, 
                    image_results
                )
                final_results = [f"{CLOUDFRONT_BASE}/{res['path']}" for res in deduplicated_results]
            else:
                final_results = []
            
            return jsonify({"images": final_results[:200]})
            
        except Exception as e:
            logger.error(f"Error in _process_without_flag: {str(e)}")
            return jsonify({"images": []}), 500
    
    def __del__(self):
        """
        Cleanup khi object bị destroy
        """
        self.executor.shutdown(wait=True)
    
    def shutdown(self):
        """
        Explicit method để shutdown executor
        """
        self.executor.shutdown(wait=True)

# Cách sử dụng:
# search_service = SearchService(max_workers=6)
# 
# @app.route('/search', methods=['POST'])
# async def search_endpoint():
#     return await search_service.process_with_executor(request)
#
# # Khi app shutdown:
# search_service.shutdown()
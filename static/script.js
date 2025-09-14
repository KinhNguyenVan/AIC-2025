document.addEventListener("DOMContentLoaded", () => {
    let videoMapping = {};

    async function loadVideoMapping() {
        try {
            const res = await fetch("/url_fps_mapping.json");
            videoMapping = await res.json();
        } catch (err) {
            console.error("Failed to load url_fps_mapping.json", err);
        }
    }

    loadVideoMapping();

    // const imageInput = document.getElementById("imageInput");
    const imageContainer = document.getElementById("imageContainer");
    const exportBtn = document.getElementById("exportCsvBtn");
    const queryInput = document.querySelector(".input-group input");

    const sidebar = document.getElementById("frameSidebar");
    const content = document.getElementById("sidebarContent");
    const toggleBtn = document.getElementById("toggleSidebarBtn");

    // Lưu danh sách ảnh được chọn theo thứ tự tick
    let selectedImages = [];


    const videoInput = document.getElementById("videoInput");
    const frameInput = document.getElementById("frameInput");
    const frameResult = document.getElementById("frameResult");
    const showFrameBtn = document.getElementById("showFrameBtn");
    const openVideoBtn2 = document.getElementById("openVideoBtn2");

    showFrameBtn.addEventListener("click", async () => {
        const video = videoInput.value.trim();
        const frame = frameInput.value.trim();

        if (!video || !frame) {
            alert("Please enter both video name and frame number!");
            return;
        }

        // Build frame URL (CloudFront hoặc S3)
        const frameUrl = `https://d1zgby2rss028i.cloudfront.net/${video}/${frame}.webp`;

        // Hiện kết quả
        frameResult.innerHTML = `
            <div class="card">
                <img src="${frameUrl}" class="card-img-top" style="max-height:200px; object-fit:contain;">
                <div class="card-body p-2 text-center">
                    <small>${video}/${frame}.webp</small>
                </div>
            </div>
        `;

        // Đồng thời renderImages để có thể tick/select
        // renderImages([frameUrl]);
    });

    openVideoBtn2.addEventListener("click", async () => {
        const video = videoInput.value.trim();
        const frame = frameInput.value.trim();

        if (!video || !frame) {
            alert("Please enter both video name and frame number!");
            return;
        }

        // Lấy video_name từ cuối đường dẫn: L30_V001
        const videoName = video.split("/").pop();
        console.log("Video name:", videoName);

        try {
            const mapping = Array.isArray(videoMapping) 
                ? videoMapping.find(m => m.video_name === videoName)
                : null;

            if (!mapping) {
                alert(`Không tìm thấy video_name ${videoName} trong url_fps_mapping.json`);
                return;
            }

            const frameNumber = parseInt(frame, 10);
            const fps = mapping.fps || 30;
            const seconds = Math.floor(frameNumber / fps);

            // Mở link youtube với timestamp
            // const youtubeUrl = `${mapping.watch_url}&t=${seconds}s`;
            // window.open(youtubeUrl, "_blank");

            console.log("Opening video:", mapping.watch_url, "at", seconds, "seconds");
            // 🚀 Mở video trong modal thay vì tab mới
            openYouTubeModal(videoName, seconds);
        } catch (err) {
            console.error(err);
            alert("Failed to open video!");
        }
    });



    // Hàm render ảnh ra imageContainer
    function renderImages(urls) {
        imageContainer.innerHTML = "";
        if (!urls || urls.length === 0) {
            imageContainer.innerHTML = "<p>No images found.</p>";
            exportBtn.classList.add("d-none");
            return;
        }

        urls.forEach(url => {
            const div = document.createElement("div");
            div.className = "col p-2 text-center";
            div.innerHTML = `
                <div class="card position-relative">
                    <img src="${url}" class="card-img-top main-img" style="height:140px; object-fit:cover;" data-url="${url}">
                    <div class="card-body p-2">
                        <input type="checkbox" class="form-check-input me-1 selectImg" data-url="${url}">
                        <small>${url.split('/').slice(-2).join('/')}</small>
                    </div>
                    <!-- badge hiển thị thứ tự -->
                    <span class="badge bg-primary position-absolute top-0 start-0 m-1 order-badge d-none"></span>
                </div>
            `;
            imageContainer.appendChild(div);
        });

        // Gắn sự kiện tick
        bindCheckboxEvents();

        // Gắn sự kiện right-click (context menu) cho ảnh
        document.querySelectorAll(".main-img").forEach(img => {
            img.addEventListener("contextmenu", (e) => {
                e.preventDefault();
                showContextMenu(e.pageX, e.pageY, img.dataset.url);
            });
        });


        exportBtn.classList.remove("d-none");
    }

    function renderSidebar(urls, currentUrl) {
        //const sidebar = document.getElementById("frameSidebar");
        const currentFrame = document.getElementById("currentFrame");
        const container = document.getElementById("sidebarImages");
        const sidebarContent = document.getElementById("sidebarContent");

        // expand sidebar
        sidebar.style.width = "400px";
        sidebarContent.style.display = "block";

        // show current keyframe
        currentFrame.innerHTML = `
            <img src="${currentUrl}" class="img-fluid rounded mb-2">
            <p class="small text-muted">${currentUrl.split('/').pop()}</p>
        `;
        //container.style.display = "block";
        container.innerHTML = "";
        urls.forEach(url => {
            const div = document.createElement("div");
            div.className = "col";
            div.innerHTML = `
                <div class="card position-relative">
                    <img src="${url}" class="card-img-top side-img" style="height:100px; object-fit:cover;" data-url="${url}">
                    <div class="card-body p-1 text-center">
                        <input type="checkbox" class="form-check-input selectImg" data-url="${url}">
                        <small>${url.split('/').slice(-2).join('/')}</small>
                    </div>
                    <span class="badge bg-success position-absolute top-0 start-0 m-1 order-badge d-none"></span>
                </div>
            `;
            container.appendChild(div);
        });

        // Áp dụng lại logic tick cho checkbox trong sidebar
        bindCheckboxEvents();

        // Gắn sự kiện right-click cho ảnh trong sidebar
        document.querySelectorAll(".side-img").forEach(img => {
            img.addEventListener("contextmenu", (e) => {
                e.preventDefault();
                showContextMenu(e.pageX, e.pageY, img.dataset.url);
            });
        });
    }

    const contextMenu = document.getElementById("contextMenu");
    const viewFramesBtn = document.getElementById("viewFramesBtn");
    const copyUrlBtn = document.getElementById("copyUrlBtn");
    let contextTargetUrl = null; // lưu URL đang right click

    function showContextMenu(x, y, url) {
        contextTargetUrl = url;
        contextMenu.style.left = `${x}px`;
        contextMenu.style.top = `${y}px`;
        contextMenu.style.display = "block";
    }

    function hideContextMenu() {
        contextMenu.style.display = "none";
    }

    // Click ngoài menu sẽ ẩn nó
    document.addEventListener("click", () => hideContextMenu());

    // Nút xem frames
    viewFramesBtn.addEventListener("click", async () => {
        if (!contextTargetUrl) return;
        hideContextMenu();

        const spinner = document.getElementById("sidebarSpinner");
        const container = document.getElementById("sidebarImages");
        container.innerHTML = ""; // xoá ảnh cũ
        spinner.classList.remove("d-none"); // hiện spinner

        try {
            const res = await fetch(`/frames?url=${encodeURIComponent(contextTargetUrl)}&prev=25&next=25`);
            const data = await res.json();

            renderSidebar(data.frames, contextTargetUrl);
        } catch (err) {
            console.error("Lỗi khi load frames:", err);
            alert("Không thể tải frames!");
        } finally {
            spinner.classList.add("d-none"); // ẩn spinner
        }
    });


    // Nút copy URL
    copyUrlBtn.addEventListener("click", () => {
        if (!contextTargetUrl) return;
        navigator.clipboard.writeText(contextTargetUrl);
        hideContextMenu();
    });


    function bindCheckboxEvents() {
        document.querySelectorAll(".selectImg").forEach(cb => {
            cb.removeEventListener("change", checkboxHandler); // tránh gắn trùng
            cb.addEventListener("change", checkboxHandler);
        });
    }

    function checkboxHandler(e) {
        const cb = e.target;
        const url = cb.dataset.url;
        const badge = cb.closest(".card").querySelector(".order-badge");

        if (cb.checked) {
            selectedImages.push(url);
        } else {
            selectedImages = selectedImages.filter(u => u !== url);
        }

        // Cập nhật badge
        document.querySelectorAll(".selectImg").forEach(c => {
            const b = c.closest(".card").querySelector(".order-badge");
            const idx = selectedImages.indexOf(c.dataset.url);
            if (idx !== -1) {
                b.textContent = idx + 1;
                b.classList.remove("d-none");
            } else {
                b.classList.add("d-none");
            }
        });

        // 🔹 Update sidebar trái
        renderSelectedSidebar();
    }


    function renderSelectedSidebar() {
        const container = document.getElementById("selectedList");
        container.innerHTML = "";

        selectedImages.forEach((url, idx) => {
            let prefix = url.split('/').slice(-2).join('/');
            let div = document.createElement("div");
            div.className = "col";
            div.innerHTML = `
                <div class="card">
                    <img src="${url}" class="card-img-top" style="height:60px; object-fit:cover;">
                    <div class="card-body p-1 text-center">
                        <input type="checkbox" class="form-check-input selectedSidebarCb" 
                            data-url="${url}" checked>
                        <small>${idx + 1}. ${prefix}</small>
                    </div>
                </div>
            `;
            container.appendChild(div);
        });

        // Gắn event cho tickbox trong sidebar
        document.querySelectorAll(".selectedSidebarCb").forEach(cb => {
            cb.addEventListener("change", sidebarCheckboxHandler);
        });
    }

    function sidebarCheckboxHandler(e) {
        const url = e.target.dataset.url;
        if (!e.target.checked) {
            // Bỏ chọn: remove khỏi selectedImages
            selectedImages = selectedImages.filter(u => u !== url);

            // Đồng bộ: bỏ tick trong grid chính nếu có
            const gridCb = document.querySelector(`.selectImg[data-url="${url}"]`);
            if (gridCb) {
                gridCb.checked = false;
                gridCb.dispatchEvent(new Event("change")); // gọi lại logic badge
            }

            // Update lại sidebar
            renderSelectedSidebar();
        }
    }


    const openVideoBtn = document.getElementById("openVideoBtn");

    openVideoBtn.addEventListener("click", () => {
        if (!contextTargetUrl) return;
        hideContextMenu();

        // Lấy video_name từ URL, ví dụ .../L30_V001/000037.webp
        const parts = contextTargetUrl.split("/");
        const videoName = parts[parts.length - 2]; // L30_V001
        const fileName = parts[parts.length - 1];  // 000037.webp

        const mapping = Array.isArray(videoMapping) 
            ? videoMapping.find(m => m.video_name === videoName)
            : null;

        if (!mapping) {
            alert(`Không tìm thấy video_name ${videoName} trong url_fps_mapping.json`);
            return;
        }

        // Lấy frame số
        const frameNumber = parseInt(fileName.replace(/\D/g, ""), 10);
        const fps = mapping.fps || 30;
        const seconds = Math.floor(frameNumber / fps);

        // Mở link youtube với timestamp
        // const youtubeUrl = `${mapping.watch_url}&t=${seconds}s`;
        // window.open(youtubeUrl, "_blank");

        //console.log("Opening video:", mapping.watch_url, "at", seconds, "seconds");
        // 🚀 Mở video trong modal thay vì tab mới
        openYouTubeModal(videoName, seconds);
    });

    function openYouTubeModal(videoName, startSeconds = 0) {
        currentVideoName = videoName;

        const mapping = Array.isArray(videoMapping) 
            ? videoMapping.find(m => m.video_name === videoName)
            : null;

        if (!mapping) {
            alert(`Không tìm thấy video_name ${videoName} trong url_fps_mapping.json`);
            return;
        }

        const videoId = new URL(mapping.watch_url).searchParams.get("v");
        player.loadVideoById({ videoId: videoId, startSeconds: startSeconds });

        const modal = new bootstrap.Modal(document.getElementById('youtubeModal'));
        modal.show();
    }

    document.getElementById("getFrameBtn").addEventListener("click", () => {
        if (!player || !currentVideoName) return;
        player.pauseVideo(); // ⏸ dừng lại

        const mapping = videoMapping.find(m => m.video_name === currentVideoName);
        const fps = mapping?.fps || 30;

        const seconds = player.getCurrentTime();
        const frame = Math.round(seconds * fps);

        // Copy vào clipboard luôn
        navigator.clipboard.writeText(seconds).then(() => {
            alert(`🎬 Video: ${currentVideoName}\n⏱ Seconds: ${seconds.toFixed(3)}\n🖼 Frame: ${frame}\n(Đã copy vào clipboard)`);
        });
    });


    

    toggleBtn.addEventListener("click", () => {
        if (sidebar.style.width === "40px") {
            sidebar.style.width = "400px";
            content.style.display = "block";
            toggleBtn.innerHTML = "&laquo;"; // arrow left
        } else {
            sidebar.style.width = "40px";
            content.style.display = "none";
            toggleBtn.innerHTML = "&raquo;"; // arrow right
        }
    });


    // Khi Enter query
    queryInput.addEventListener("keydown", async (e) => {
        if (e.key === "Enter") {
            const query = queryInput.value.trim();
            if (!query) return;

            // Clear tickbox
            selectedImages = [];
            document.querySelectorAll(".selectImg").forEach(cb => {
                cb.checked = false;
                const badge = cb.closest(".card").querySelector(".order-badge");
                if (badge) badge.classList.add("d-none");
            });

            const flagValue = document.getElementById("flagInput").value.trim();
            const flag = document.getElementById("flagCheckbox").checked;

            const spinner = document.getElementById("loadingSpinner");
            const container = document.getElementById("imageContainer");
            container.innerHTML = ""; // clear ảnh cũ
            spinner.classList.remove("d-none"); // show spinner

            try {
                const res = await fetch("/query", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        query: query,
                        flag: flag,
                        flagValue: flagValue
                    })
                });

                const data = await res.json();
                renderImages(data.images);
            } catch (err) {
                console.error("Error fetching images:", err);
                alert("Failed to fetch images!");
            } finally {
                spinner.classList.add("d-none"); // hide spinner
            }
        }
    });


    // Export CSV (chỉ ảnh tick theo thứ tự)
    exportCsvBtn.addEventListener("click", () => {
        if (selectedImages.length === 0) {
            alert("No images selected!");
            return;
        }

        // Lấy tên file từ input
        let filename = document.getElementById("filenameInput").value.trim();
        if (!filename) filename = "results.csv";
        if (!filename.endsWith(".csv")) filename += ".csv";

        // Lấy answer input
        let answer = document.getElementById("answerInput").value.trim();

        // Tạo nội dung CSV
        let rows = selectedImages.map(url => {
            // Lấy prefix + filename (VD: L28_V016/028779.webp)
            let prefix = url.split('/').slice(-2).join('/');

            // Tách thành ID + number
            let [folder, file] = prefix.split('/');
            let id = folder; // ví dụ: L28_V016
            let number = parseInt(file.replace(/\D/g, "")); // lấy số từ 028779.webp → 28779

            if (answer) {
                return `${id}, ${number}, "${answer}"`;
            } else {
                return `${id}, ${number}`;
            }
        });

        let csvContent = "data:text/csv;charset=utf-8," + rows.join("\n");
        const encodedUri = encodeURI(csvContent);

        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });

    document.getElementById("generateCsvBtn").addEventListener("click", () => {
        const filename = document.getElementById("csvFilenameInput").value.trim() || "result.csv";
        const videoName = document.getElementById("videoNameInput").value.trim();
        const secondsStr = document.getElementById("secondsInput").value.trim();
        const rowCount = parseInt(document.getElementById("rowCountInput").value) || 50;
        const offset = parseInt(document.getElementById("offsetInput").value) || 3;

        if (!videoName || !secondsStr) {
            alert("Please enter video name and frames!");
            return;
        }

        const mapping = Array.isArray(videoMapping) 
                ? videoMapping.find(m => m.video_name === videoName)
                : null;

        if (!mapping) {
            alert(`Không tìm thấy video_name ${videoName} trong url_fps_mapping.json`);
            return;
        }

        const fps = mapping.fps || 30;
        // 🔄 Hàm parse seconds hỗ trợ cả 2 định dạng: giây hoặc phút:giây
        function parseTimeStr(str) {
            str = str.trim();
            if (str.includes(":")) {
                const parts = str.split(":");
                if (parts.length === 2) {
                    const minutes = parseFloat(parts[0]);
                    const seconds = parseFloat(parts[1]);
                    return minutes * 60 + seconds;
                }
            }
            return parseFloat(str);
        }

        // 🎯 Chuyển seconds (hỗn hợp) -> frames
        const baseFrames = secondsStr.split(",")
            .map(s => parseTimeStr(s))
            .filter(val => !isNaN(val))
            .map(sec => Math.round(sec * fps));

        if (baseFrames.length === 0) {
            alert("Không parse được seconds nào hợp lệ!");
            return;
        }

        // 📄 Sinh các row
        let rows = [];
        rows.push(`${videoName}, ${baseFrames.join(", ")}`); // row gốc

        for (let i = 1; i <= rowCount - 1; i++) {
            const delta = i * offset;

            // row cộng
            const plusRow = baseFrames.map(f => f + delta);
            rows.push(`${videoName}, ${plusRow.join(", ")}`);

            // row trừ
            const minusRow = baseFrames.map(f => f - delta);
            rows.push(`${videoName}, ${minusRow.join(", ")}`);
        }

        // 📤 Xuất CSV
        const csvContent = "data:text/csv;charset=utf-8," + rows.join("\n");
        const encodedUri = encodeURI(csvContent);

        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });

});


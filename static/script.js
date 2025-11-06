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
    const resultTypeSelect = document.getElementById("resultType");
    const qaAnswerGroup = document.getElementById("qaAnswerGroup");
    const qaAnswerInput = document.getElementById("qaAnswerInput");
    const exportResultBtn = document.getElementById("exportResultBtn");
    const sendToSubmissionBtn = document.getElementById("sendToSubmissionBtn");
    const resultOutput = document.getElementById("resultOutput");
    let lastPreparedBody = null;
    const queryInput = document.querySelector(".input-group input");

    const sidebar = document.getElementById("frameSidebar");
    const content = document.getElementById("sidebarContent");
    const toggleBtn = document.getElementById("toggleSidebarBtn");

    // Lưu danh sách ảnh được chọn theo thứ tự tick
    let selectedImages = [];


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


        if (exportBtn) exportBtn.classList.remove("d-none");
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

            const flagInputValue = document.getElementById("flagInput").value.trim();
            
            // Lấy các topic được chọn từ checkbox (trả về danh sách tên topic)
            const selectedTopics = [];
            document.querySelectorAll(".topic-checkbox:checked").forEach(cb => {
                const topic = cb.dataset.topic;
                selectedTopics.push(topic);
            });

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
                        flagValue: flagInputValue,
                        topics: selectedTopics
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


    // Toggle answer input theo kiểu QA
    if (resultTypeSelect) {
        resultTypeSelect.addEventListener("change", () => {
            const isQA = resultTypeSelect.value === "qa";
            if (qaAnswerGroup) {
                if (isQA) qaAnswerGroup.classList.remove("d-none");
                else qaAnswerGroup.classList.add("d-none");
            }
        });
    }

    function getVideoAndFrame(url) {
        const parts = url.split("/");
        const videoName = parts[parts.length - 2];
        const fileName = parts[parts.length - 1];
        const frameNumber = parseInt(fileName.replace(/\D/g, ""), 10);
        return { videoName, frameNumber };
    }

    function getFpsForVideo(videoName) {
        const mapping = Array.isArray(videoMapping)
            ? videoMapping.find(m => m.video_name === videoName)
            : null;
        return mapping?.fps || 30;
    }

    function frameToMs(videoName, frameNumber) {
        const fps = getFpsForVideo(videoName);
        return Math.round((frameNumber / fps) * 1000);
    }

    if (exportResultBtn) {
        exportResultBtn.addEventListener("click", () => {
            const type = resultTypeSelect?.value || "kis";
            // Thu thập các cặp (video, frame)
            const items = selectedImages.map(url => getVideoAndFrame(url));

            if (type === "kis") {
                if (items.length !== 2) {
                    alert("KIS: Cần chọn đúng 2 frame.");
                    return;
                }
                const sameVideo = items[0].videoName === items[1].videoName;
                if (!sameVideo) {
                    alert("KIS: 2 frame phải thuộc cùng 1 video.");
                    return;
                }
                const videoName = items[0].videoName;
                const startMs = frameToMs(videoName, items[0].frameNumber);
                const endMs = frameToMs(videoName, items[1].frameNumber);
                const body = {
                    answerSets: [
                        {
                            answers: [
                                {
                                    mediaItemName: videoName,
                                    start: startMs,
                                    end: endMs
                                }
                            ]
                        }
                    ]
                };
                resultOutput.value = JSON.stringify(body, null, 2);
                lastPreparedBody = body;
            } else if (type === "qa") {
                if (items.length !== 1) {
                    alert("QA: Cần chọn đúng 1 frame.");
                    return;
                }
                const answer = qaAnswerInput?.value?.trim();
                if (!answer) {
                    alert("QA: Vui lòng nhập answer.");
                    return;
                }
                const { videoName, frameNumber } = items[0];
                const frameMs = frameToMs(videoName, frameNumber);
                const qaText = `QA-${answer}-${videoName}-${frameMs}`;
                const body = {
                    answerSets: [
                        {
                            answers: [
                                {
                                    text: qaText
                                }
                            ]
                        }
                    ]
                };
                resultOutput.value = JSON.stringify(body, null, 2);
                lastPreparedBody = body;
            } else if (type === "trake") {
                if (items.length === 0) {
                    alert("Trake: Cần chọn ít nhất 1 frame.");
                    return;
                }
                // Yêu cầu: các frame phải cùng 1 video theo ví dụ
                const baseVideo = items[0].videoName;
                const allSame = items.every(i => i.videoName === baseVideo);
                if (!allSame) {
                    alert("Trake: Tất cả frame phải cùng 1 video.");
                    return;
                }
                const frameList = items.map(i => i.frameNumber).join(",");
                const trText = `TR-${baseVideo}-${frameList}`;
                const body = {
                    answerSets: [
                        {
                            answers: [
                                {
                                    text: trText
                                }
                            ]
                        }
                    ]
                };
                resultOutput.value = JSON.stringify(body, null, 2);
                lastPreparedBody = body;
            }
        });
    }

    // Chuyển body sang trang nộp bài
    if (sendToSubmissionBtn) {
        sendToSubmissionBtn.addEventListener("click", () => {
            if (!lastPreparedBody) {
                alert("Vui lòng xuất kết quả trước khi gửi sang trang nộp bài.");
                return;
            }
            try {
                localStorage.setItem("preparedSubmissionBody", JSON.stringify(lastPreparedBody));
                window.location.href = "/submission";
            } catch (e) {
                alert("Không thể lưu body vào localStorage.");
            }
        });
    }

});


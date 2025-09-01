document.addEventListener("DOMContentLoaded", () => {
    const imageInput = document.getElementById("imageInput");
    const imageContainer = document.getElementById("imageContainer");
    const exportBtn = document.getElementById("exportCsvBtn");
    const queryInput = document.querySelector(".input-group input");

    const sidebar = document.getElementById("frameSidebar");
    const content = document.getElementById("sidebarContent");
    const toggleBtn = document.getElementById("toggleSidebarBtn");

    // Lưu danh sách ảnh được chọn theo thứ tự tick
    let selectedImages = [];

    // Upload images (demo DB)
    imageInput.addEventListener("change", async () => {
        const files = imageInput.files;
        const formData = new FormData();
        for (let file of files) {
            formData.append("images", file);
        }
        await fetch("/upload", { method: "POST", body: formData });
        loadDB();
    });

    // Load DB images (ban đầu hiển thị DB local)
    async function loadDB() {
        const res = await fetch("/db");
        const data = await res.json();
        renderImages(data.images.map(name => `/image/${name}`));
    }
    loadDB();

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
            img.addEventListener("contextmenu", async (e) => {
                e.preventDefault();
                const url = img.dataset.url;

                // Giả sử có API getFrames(url, nPrev, nNext)
                const res = await fetch(`/frames?url=${encodeURIComponent(url)}&prev=25&next=25`);
                const data = await res.json(); // data.frames = [list of frame URLs]

                renderSidebar(data.frames, url);
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
            img.addEventListener("contextmenu", async (e) => {
                e.preventDefault();
                const url = img.dataset.url;

                // Gọi API lấy 25 frames trước/sau
                const res = await fetch(`/frames?url=${encodeURIComponent(url)}&prev=25&next=25`);
                const data = await res.json();

                // Render lại sidebar với ảnh này làm current
                renderSidebar(data.frames, url);
            });
        });
    }

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

            // 🔹 Clear hết tickbox và reset selectedImages
            selectedImages = [];
            document.querySelectorAll(".selectImg").forEach(cb => {
                cb.checked = false;
                const badge = cb.closest(".card").querySelector(".order-badge");
                if (badge) badge.classList.add("d-none");
            });

            const flag = document.getElementById("flagCheckbox").checked; // true/false

            const res = await fetch("/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: query,
                    flag: flag
                })
            });

            const data = await res.json();

            renderImages(data.images); // hiển thị kết quả query trong imageContainer
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
});


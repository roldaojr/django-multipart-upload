document.addEventListener("DOMContentLoaded", () => {
  document
    .querySelectorAll("input[type=file].multipart")
    .forEach((inputElement) => {
      const form = inputElement.closest("form");
      const dzElement = inputElement.parentElement;
      const templateElement = dzElement.querySelector(".preview-template");
      const previewsElement = dzElement.querySelector(".dz-files");
      const submitButton = form.querySelector(
        "button[type=submit], input[type=submit]"
      );
      // values
      const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]").value;
      const chunkSize = parseInt(inputElement.getAttribute("data-chunk-size"));
      const uploadUrl = inputElement
        .getAttribute("data-upload-url")
        .trimEnd("/");
      // change element type do hidden
      inputElement.setAttribute("type", "hidden");
      const dropzone = new Dropzone(dzElement, {
        method: "put",
        timeout: 3600000,
        headers: {
          "X-CSRFToken": csrfToken,
          Accept: null,
          "Content-Type": null,
        },
        chunking: true,
        forceChunking: true,
        chunkSize: chunkSize,
        parallelUploads: 4,
        parallelChunkUploads: true,
        retryChunks: true,
        retryChunksLimit: 3,
        maxFilesize: 100 * 1024,
        autoProcessQueue: false,
        createImageThumbnails: false,
        maxFiles: 1,
        binaryBody: true,
        previewTemplate: templateElement ? templateElement.innerHTML : "",
        previewsContainer: dzElement,
        clickable: dzElement,
        init: function () {
          const dropzone = this;
          form._submit = form.submit;
          form.addEventListener("submit", function (e) {
            e.preventDefault();
            form.submit();
          });
          form.submit = () => {
            if (
              dropzone.getQueuedFiles().length == 0 &&
              inputElement.getAttribute("data-initial") == "true"
            ) {
              // has initial file and no queued files. submit the form
              form._submit();
            } else {
              // call the queue
              dropzone.processQueue();
            }
            dropzone.processQueue();
          };
          this.on("addedfile", function (file) {
            // remove extra files
            while (this.files.length > this.options.maxFiles) {
              this.removeFile(this.files[0]);
            }
          });
          this.on("sending", function (file) {
            submitButton.setAttribute("disabled", "");
          });
          this.on("complete", function (file) {
            submitButton.removeAttribute("disabled");
            if (file.status == "success") {
              form._submit();
            }
          });
          this.on("success", function (file) {
            inputElement.value = `${file.name};${file.upload.multipart.server_id}`;
          });
        },
        accept: function (file, done) {
          // get multipart upload URL
          const baseURL = uploadUrl;
          const url = new URL(`${baseURL}/${file.name}`, window.location.href);
          const partCount = Math.ceil(file.upload.total / chunkSize);
          url.searchParams.set("partCount", partCount);
          fetch(url)
            .then((res) => res.json())
            .then((data) => {
              file.upload.multipart = data;
              this.emit("acceptedfile", file);
              done();
            })
            .catch((err) => {
              this.emit("rejectedfile", err, file);
              done(err);
            });
        },
        url: function (files) {
          var upload = files[0].upload;
          return upload.multipart.parts_urls[upload.chunks.length - 1];
        },
        chunksUploaded: function (file, done) {
          let parts = file.upload.chunks.map((chunk) => {
            const arr = chunk.responseHeaders.trim().split(/[\r\n]+/);
            // Create a map of header names to values
            const headerMap = {};
            arr.forEach((line) => {
              const [_, header, value] = line.split(/^([\w-]+):[ ]/);
              headerMap[header] = value;
            });
            return {
              ETag: headerMap["etag"].replaceAll('"', ""),
              PartNumber: chunk.index + 1,
            };
          });
          fetch(file.upload.multipart.complete_url, {
            method: "post",
            headers: {
              "Content-type": "application/json",
              "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({ Parts: parts }),
          })
            .then((response) => {
              if (!response.ok) {
                console.error(response.content);
                return Promise.reject("Erro ao finalizar upload");
              }
              done();
            })
            .catch((err) => done(err));
        },
      });
    });
});

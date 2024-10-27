document.addEventListener("DOMContentLoaded", () => {
  const multipartFileInputs = {};
  document
    .querySelectorAll("input[type=file].multipart")
    .forEach((inputElement) => {
      // ignore formset input template
      if (inputElement.name.includes("__prefix__")) return;
      // get elements
      const form = inputElement.closest("form");
      const dzElement = inputElement.parentElement;
      const templateElement = dzElement.querySelector(".preview-template");
      const previewsElement = dzElement.querySelector(".dz-files");
      const noFileElement = dzElement.querySelector(".dz-no-file");
      const submitButton = form.querySelector(
        "button[type=submit], input[type=submit]"
      );
      // get widget values
      const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]").value;
      const chunkSize = parseInt(inputElement.getAttribute("data-chunk-size"));
      const uploadUrl = inputElement
        .getAttribute("data-upload-url")
        .trimEnd("/");
      // change element type do hidden
      inputElement.setAttribute("type", "hidden");
      // init dropzone
      const dropzone = new Dropzone(inputElement, {
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
        previewsContainer: previewsElement,
        clickable: dzElement,
        init: function () {
          this.on("addedfile", function (file) {
            // remove extra files
            while (this.files.length > this.options.maxFiles) {
              this.removeFile(this.files[0]);
            }
            noFileElement.style.display = "none";
          });
          this.on("removedfile", function (file) {
            noFileElement.style.display = "";
          });
          this.on("sending", function (file) {
            submitButton.setAttribute("disabled", "");
          });
          this.on("success", function (file) {
            inputElement.value = `${file.name};${file.upload.multipart.server_id}`;
          });
          this.on("complete", function (file) {
            submitButton.removeAttribute("disabled");
            multipartFileInputs[inputElement.name].status = "complete";
            form.submit();
          });
        },
        accept: function (file, done) {
          // get multipart upload URL
          const baseURL = uploadUrl;
          const url = new URL(`${baseURL}/${file.name}`, window.location.href);
          const partCount = Math.ceil(file.upload.total / chunkSize);
          url.searchParams.set("partCount", partCount);
          fetch(url)
            .then((res) => {
              if (res.status == 200) return res.json();
              throw new Error(
                `Init multipart upload failed with status ${res.status}`
              );
            })
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
      multipartFileInputs[inputElement.name] = {
        dropzone: dropzone,
        element: inputElement,
        status: "pedinng",
      };

      if (form._mpfi_submit) return;
      // add submit handler
      form._mpfi_submit = form.submit;
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        form.submit();
      });
      form.submit = () => {
        Object.values(multipartFileInputs).forEach((input) => {
          if (
            input.dropzone.getQueuedFiles().length == 0 &&
            input.status != "complete"
          ) {
            // has initial file and no queued files. set status to complete
            input.status = "complete";
          } else {
            // call the queue
            input.dropzone.processQueue();
          }
        });
        if (
          Object.values(multipartFileInputs).every(
            (i) => i.status == "complete"
          )
        ) {
          return form._mpfi_submit();
        }
      };
    });
});

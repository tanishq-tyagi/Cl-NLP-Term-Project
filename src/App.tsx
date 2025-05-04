import { useState, useRef, useEffect } from "react";

export function App() {
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [outputFile, setOutputFile] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Check for existing output files when the component mounts
  useEffect(() => {
    const checkForOutputFiles = async () => {
      try {
        const response = await fetch("http://localhost:5000/api/files");
        const data = await response.json();

        if (data.files && data.files.length > 0) {
          // Get the latest file based on the naming convention (should be the highest number)
          const latestFile = data.files.sort().pop();
          if (latestFile) {
            setOutputFile(latestFile);
            setMessage("Previous output file available for download");
          }
        }
      } catch (error) {
        console.error("Error checking for output files:", error);
      }
    };

    checkForOutputFiles();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFiles(e.target.files);
      setMessage(`${e.target.files.length} file(s) selected`);
    } else {
      setSelectedFiles(null);
      setMessage(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFiles || selectedFiles.length === 0) {
      setMessage("Please select files first");
      return;
    }

    setIsUploading(true);
    setMessage("Uploading files...");

    const formData = new FormData();
    for (let i = 0; i < selectedFiles.length; i++) {
      formData.append("files[]", selectedFiles[i]);
    }

    try {
      const response = await fetch("http://localhost:5000/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message);
        // Reset file input
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
        setSelectedFiles(null);
      } else {
        setMessage(`Error: ${data.error}`);
      }
    } catch (error) {
      setMessage(
        `Upload failed: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    } finally {
      setIsUploading(false);
    }
  };

  const handleProcess = async () => {
    setIsProcessing(true);
    setMessage("Processing files...");
    setOutputFile(null); // Reset the output file state when starting a new process

    try {
      const response = await fetch("http://localhost:5000/api/process", {
        method: "POST",
      });

      const data = await response.json();

      if (response.ok) {
        setMessage("Processing complete!");
        setOutputFile(data.filename);
      } else {
        setMessage(`Error: ${data.error}`);
      }
    } catch (error) {
      setMessage(
        `Processing failed: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = () => {
    if (outputFile) {
      window.location.href = `http://localhost:5000/api/download/${outputFile}`;
    } else {
      setMessage("No file available for download");
    }
  };

  return (
    <div className="container flex justify-center flex-col items-center">
      <div className="dashedContainer flex flex-col justify-center items-center p-10 rounded-md m-8">
        <h1>Noterizer</h1>
        <p className="mb-2">Notes Generation and Management Application</p>
        <span className="mb-15">One Click. Perfect Notes. Every Time.</span>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="file-input file-input-success file-input-sm mt-8"
          onChange={handleFileChange}
        />

        {message && (
          <div className="mt-2 text-center">
            <span>{message}</span>
          </div>
        )}

        <div className="flex w-full max-w-xs mt-4">
          <button
            className={`btn ${
              isUploading ? "btn-error" : "btn-success"
            } flex-1 mr-2 btn-sm`}
            onClick={handleUpload}
            disabled={isUploading || !selectedFiles}
          >
            {isUploading ? "Uploading..." : "Upload"}
          </button>
          <button
            className={`btn ${
              isProcessing ? "btn-error" : "btn-success"
            } flex-1 mx-2 btn-sm`}
            onClick={handleProcess}
            disabled={isProcessing}
          >
            {isProcessing ? "Processing..." : "Process"}
          </button>
          <button
            className={`btn ${
              !outputFile ? "btn-error" : "btn-success"
            } flex-1 ml-2 btn-sm`}
            onClick={handleDownload}
            disabled={!outputFile}
          >
            Download
          </button>
        </div>
      </div>
      <footer className="footer sm:footer-horizontal footer-center bg-base-100 text-base-content p-2">
        <span>
          Application created by Tanishq Tyagi :D @ {new Date().getFullYear()}
        </span>
      </footer>
    </div>
  );
}

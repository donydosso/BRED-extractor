package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
)

const (
	uploadPath   = "/app/tmp/uploads"
	outputPath   = "/app/tmp/output"
	pythonScript = "/app/python/app.py"
	jsonDataPath = "/app/tmp/output/transactions.json"
	certFile     = "/app/certs/cert.pem"
	keyFile      = "/app/certs/key.pem"
)

func init() {
	os.MkdirAll(uploadPath, 0755)
	os.MkdirAll(outputPath, 0755)
}

func uploadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	file, header, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Error retrieving the file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Create the upload file
	uploadedFile := filepath.Join(uploadPath, header.Filename)
	out, err := os.Create(uploadedFile)
	if err != nil {
		http.Error(w, "Unable to create the file", http.StatusInternalServerError)
		return
	}
	defer out.Close()

	_, err = io.Copy(out, file)
	if err != nil {
		http.Error(w, "Error saving the file", http.StatusInternalServerError)
		return
	}

	// Process the PDF with Python
	excelFile := filepath.Join(outputPath, "transactions.xlsx")
	cmd := exec.Command("python3", pythonScript, uploadedFile, excelFile, jsonDataPath) // Ajout du 3ème argument
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Python script error: %s\n", output)
		http.Error(w, "Error processing PDF", http.StatusInternalServerError)
		return
	}

	// Return the processed file info
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"status":   "success",
		"filename": "transactions.xlsx",
	})
}

func previewHandler(w http.ResponseWriter, r *http.Request) {
	// Lire le fichier JSON généré par le script Python
	data, err := os.ReadFile(jsonDataPath)
	if err != nil {
		http.Error(w, "Preview data not available", http.StatusNotFound)
		return
	}

	// Déjà au format JSON, on peut l'envoyer directement
	w.Header().Set("Content-Type", "application/json")
	w.Write(data)
}

func downloadHandler(w http.ResponseWriter, r *http.Request) {
	filePath := filepath.Join(outputPath, "transactions.xlsx")

	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		http.Error(w, "File not found", http.StatusNotFound)
		return
	}

	file, err := os.Open(filePath)
	if err != nil {
		http.Error(w, "Error opening file", http.StatusInternalServerError)
		return
	}
	defer file.Close()

	w.Header().Set("Content-Disposition", "attachment; filename=transactions.xlsx")
	w.Header().Set("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

	_, err = io.Copy(w, file)
	if err != nil {
		http.Error(w, "Error sending file", http.StatusInternalServerError)
	}
}

func main() {
	http.HandleFunc("/upload", uploadHandler)
	http.HandleFunc("/preview", previewHandler)
	http.HandleFunc("/download", downloadHandler)
	http.Handle("/", http.FileServer(http.Dir("/app/frontend")))

	fmt.Println("Server started on :8443")
	//log.Fatal(http.ListenAndServeTLS(":8443", certFile, keyFile, nil))
	log.Fatal(http.ListenAndServe(":8443", nil)) // Pour le développement, on utilise HTTP non sécurisé
}

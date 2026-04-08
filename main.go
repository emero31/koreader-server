package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"sync"
)

type Progress struct {
	DocumentHash string  `json:"document_hash"`
	Percentage   float64 `json:"percentage"`
	Progress     string  `json:"progress"`
	DeviceID     string  `json:"device_id"`
	DeviceName   string  `json:"device_name"`
	Timestamp    int64   `json:"timestamp"`
}

var (
	storage = make(map[string]Progress)
	mutex   sync.RWMutex
)

func main() {
	port := os.Getenv("PORT")
	if port == "" { port = "8081" }

	http.HandleFunc("/", handleRequest)

	log.Printf("Server startuje na porte %s...", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}

func handleRequest(w http.ResponseWriter, r *http.Request) {
	// Povolenie vsetkeho (CORS)
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization, x-auth-token")

	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	path := r.URL.Path
	log.Printf("Spracovavam: %s %s", r.Method, path)

	// 1. AUTH - KOReader sa pyta na autorizaciu
	if strings.HasSuffix(path, "/auth") {
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, `{"username":"%s","token":"fixed_token"}`, "emero31")
		return
	}

	// 2. PROGRESS - Synchronizacia pozicie
	if strings.Contains(path, "/progress") {
		// Vypreparujeme hash dokumentu z URL
		parts := strings.Split(path, "/")
		docHash := parts[len(parts)-1]

		if r.Method == http.MethodPut {
			var p Progress
			body, _ := io.ReadAll(r.Body)
			if err := json.Unmarshal(body, &p); err != nil {
				log.Printf("Chyba JSONu: %v", err)
				w.WriteHeader(http.StatusBadRequest)
				return
			}
			p.DocumentHash = docHash
			
			mutex.Lock()
			storage[docHash] = p
			mutex.Unlock()

			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusCreated)
			json.NewEncoder(w).Encode(p)
			return
		}

		if r.Method == http.MethodGet {
			mutex.RLock()
			p, ok := storage[docHash]
			mutex.RUnlock()

			if !ok {
				w.WriteHeader(http.StatusNotFound)
				return
			}
			w.Header().Set("Content-Type", "application/json")
			w.Header().Set("ETag", fmt.Sprintf("\"%s\"", docHash))
			json.NewEncoder(w).Encode(p)
			return
		}
	}

	// 3. POISTKA - Zakladna odpoved pre plugin
	w.WriteHeader(http.StatusOK)
}

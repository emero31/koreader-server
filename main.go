package main

import (
	"io"
	"log"
	"net/http"
	"os"
	"sync"
)

var (
	storage = make(map[string][]byte)
	mutex   sync.RWMutex
)

func main() {
	port := os.Getenv("PORT")
	if port == "" { port = "8081" }

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		// Pridáme hlavičky, ktoré hovoria "VŠETKO JE DOVOLENÉ"
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, PUT, POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		log.Printf("%s %s", r.Method, r.URL.Path)

		// Reakcia na Auth
		if r.URL.Path == "/auth" || r.URL.Path == "/koreader/v1/auth" || r.URL.Path == "/v1/auth" {
			w.Header().Set("Content-Type", "application/json")
			w.Write([]byte(`{"username":"emero31","token":"ok"}`))
			return
		}

		// Reakcia na Progress (Ukladanie)
		if r.Method == http.MethodPut {
			body, _ := io.ReadAll(r.Body)
			mutex.Lock()
			storage[r.URL.Path] = body
			mutex.Unlock()
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusCreated)
			w.Write(body)
			return
		}

		// Reakcia na Progress (Načítanie)
		if r.Method == http.MethodGet {
			mutex.RLock()
			val, ok := storage[r.URL.Path]
			mutex.RUnlock()
			if !ok {
				w.WriteHeader(http.StatusNotFound)
				return
			}
			w.Header().Set("Content-Type", "application/json")
			w.Write(val)
			return
		}
		w.WriteHeader(http.StatusOK)
	})

	log.Printf("Server bezi...")
	http.ListenAndServe(":"+port, nil)
}

package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strings"
	"sync"
)

type Progress struct {
	Percentage float64 `json:"percentage"`
	DeviceID   string  `json:"device_id"`
	Timestamp  int64   `json:"timestamp"`
}

var (
	storage = make(map[string]Progress)
	mutex   sync.RWMutex
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8081"
	}

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		log.Printf("Request: %s %s", r.Method, r.URL.Path)

		// 1. Odpoveď na Auth (vždy úspech)
		if strings.Contains(r.URL.Path, "/auth") {
			w.Header().Set("Content-Type", "application/json")
			w.Write([]byte(`{"username":"emero31","token":"ok"}`))
			return
		}

		// 2. Spracovanie priebehu
		if strings.Contains(r.URL.Path, "/progress") {
			key := r.URL.Path
			
			if r.Method == http.MethodPut {
				var p Progress
				json.NewDecoder(r.Body).Decode(&p)
				
				mutex.Lock()
				storage[key] = p
				mutex.Unlock()

				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusCreated)
				json.NewEncoder(w).Encode(p) // KOReader chce vidieť tie dáta späť
				return
			}

			if r.Method == http.MethodGet {
				mutex.RLock()
				p, ok := storage[key]
				mutex.RUnlock()
				
				if !ok {
					w.WriteHeader(http.StatusNotFound)
					return
				}
				w.Header().Set("Content-Type", "application/json")
				json.NewEncoder(w).Encode(p)
				return
			}
		}

		// 3. Všeobecná odpoveď OK pre čokoľvek iné
		w.WriteHeader(http.StatusOK)
	})

	log.Printf("Server bezi na porte %s...", port)
	http.ListenAndServe(":"+port, nil)
}

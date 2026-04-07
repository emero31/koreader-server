package main

import (
	"io"
	"log"
	"net/http"
	"os"
	"sync"
)

var (
	// Polička na dáta (všetko ukladáme ako čistý text/JSON)
	storage = make(map[string][]byte)
	mutex   sync.RWMutex
)

func main() {
	port := os.Getenv("PORT")
	if port == "" { port = "8081" }

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		log.Printf("Metoda: %s | Cesta: %s", r.Method, r.URL.Path)

		// 1. Ak KOReader len "klope" na Auth
		if r.URL.Path == "/auth" || r.URL.Path == "/koreader/v1/auth" {
			w.Header().Set("Content-Type", "application/json")
			w.Write([]byte(`{"username":"emero31","token":"ok"}`))
			return
		}

		// 2. Ak KOReader posiela alebo pyta data (Progress)
		key := r.URL.Path

		if r.Method == http.MethodPut {
			body, _ := io.ReadAll(r.Body)
			mutex.Lock()
			storage[key] = body
			mutex.Unlock()
			
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusCreated)
			w.Write(body) // Vratime mu presne to iste, co poslal
			return
		}

		if r.Method == http.MethodGet {
			mutex.RLock()
			val, ok := storage[key]
			mutex.RUnlock()

			if !ok {
				w.WriteHeader(http.StatusNotFound)
				return
			}
			w.Header().Set("Content-Type", "application/json")
			w.Write(val)
			return
		}

		// Poistka pre vsetko ostatne
		w.WriteHeader(http.StatusOK)
	})

	log.Printf("Dojicka nastartovana na porte %s...", port)
	http.ListenAndServe(":"+port, nil)
}

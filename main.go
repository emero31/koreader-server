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
	data  = make(map[string]Progress)
	mutex sync.RWMutex
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8081"
	}

	http.HandleFunc("/", handleAll)
	
	log.Printf("Server bezi na porte %s...", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}

func handleAll(w http.ResponseWriter, r *http.Request) {
	// 1. Povolenie pre KOReader (Auth)
	if strings.Contains(r.URL.Path, "/auth") {
		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(`{"username":"emero31","token":"ok"}`))
		return
	}

	// 2. Samotná synchronizácia (Progress)
	if strings.Contains(r.URL.Path, "/progress") {
		// Očistíme cestu, aby nám nevadili lomky navyše
		key := strings.TrimRight(r.URL.Path, "/")

		if r.Method == http.MethodGet {
			mutex.RLock()
			p, ok := data[key]
			mutex.RUnlock()
			if !ok {
				w.WriteHeader(http.StatusNotFound)
				return
			}
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(p)
			return
		}

		if r.Method == http.MethodPut {
			var p Progress
			if err := json.NewDecoder(r.Body).Decode(&p); err != nil {
				// Skúsime dekódovať aspoň to, čo príde
				log.Printf("Chyba dekodovania: %v", err)
			}
			mutex.Lock()
			data[key] = p
			mutex.Unlock()
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusCreated)
			w.Write([]byte(`{"status":"ok"}`))
			return
		}
	}

	// 3. Poistka pre všetko ostatné
	w.WriteHeader(http.StatusOK)
}

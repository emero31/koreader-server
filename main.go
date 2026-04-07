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
	
	log.Printf("Server startuje na porte %s...", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}

func handleAll(w http.ResponseWriter, r *http.Request) {
	// 1. Odpovieme na kontrolu autorizácie (vždy OK)
	if strings.Contains(r.URL.Path, "/auth") {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"username":"emero31","token":"faketoken"}`))
		return
	}

	// 2. Spracovanie samotného priebehu (Progress)
	if strings.Contains(r.URL.Path, "/progress") {
		key := r.URL.Path
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
		} else if r.Method == http.MethodPut {
			var p Progress
			if err := json.NewDecoder(r.Body).Decode(&p); err != nil {
				http.Error(w, err.Error(), http.StatusBadRequest)
				return
			}
			mutex.Lock()
			data[key] = p
			mutex.Unlock()
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusCreated)
			w.Write([]byte(`{"status":"ok"}`))
		}
		return
	}

	// 3. Pre všetko ostatné vrátime OK
	w.WriteHeader(http.StatusOK)
}

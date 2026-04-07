package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
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

	// Toto je to správne potrubie pre KOReader!
	http.HandleFunc("/koreader/v1/progress/", handleSync)
	
	log.Printf("Server bezi na porte %s...", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}

func handleSync(w http.ResponseWriter, r *http.Request) {
	// Získame názov knihy z URL
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
		w.WriteHeader(http.StatusCreated)
		fmt.Fprintf(w, `{"status":"ok"}`)
	}
}

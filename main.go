package main

import (
	"encoding/json"
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

	http.HandleFunc("/users/", handleSync)
	
	log.Printf("Server startuje na porte %s...", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}

func handleSync(w http.ResponseWriter, r *http.Request) {
	key := r.URL.Path
	if r.Method == http.MethodGet {
		mutex.RLock()
		p, ok := data[key]
		mutex.RUnlock()
		if !ok {
			http.Error(w, "Not found", http.StatusNotFound)
			return
		}
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
	}
}

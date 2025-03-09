#!/bin/bash

stop_services() {
    echo "Stoping services..."
    pkill -9 -f "flask"
}

stop_hazelcast() {
    echo "Stoping Hazelcast nodes..."
    pkill -9 -f "hazelcast"
}

stop_hazelcast
stop_services

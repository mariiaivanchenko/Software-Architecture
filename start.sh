#!/bin/bash

HAZELCAST_BIN_PATH=/Users/mariia/hazelcast-5.5.0/bin
HAZELCAST_XML_PATH=/Users/mariia/hazelcast-5.5.0/config/hazelcast.xml

load_config() {
    echo "Loading configuration file data..."
    local section=""
    while IFS='=' read -r key value; do
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)
        if [[ -z "$key" || "$key" =~ ^\s*# ]]; then
            continue
        fi

        if [[ "$key" =~ ^\[(.*)\]$ ]]; then
            section="${BASH_REMATCH[1]}"
        else
            key=$(echo "${section}_${key}" | tr '[:lower:]' '[:upper:]' | tr -d ' ')
            export "$key"="$value"
        fi
    done < configuration.ini
}


start_services() {
    echo "Running utils..."
    python3 utils.py &

    echo "Starting services..."
    # facade
    flask --app facade-service run --host 127.0.0.1 --port=5000 &

    # logging
    echo "Starting logging services..."
    for i in `seq 0 2`;
    do
        port=$((5001 + $i))
        flask --app logging-service run --host 127.0.0.1 --port=$port &
        sleep 3
    done

    # messages
    echo "Starting messages services..."
    for i in `seq 0 1`;
    do
        port=$((5004 + $i))
        flask --app messages-service run --host 127.0.0.1 --port=$port &
        sleep 3
    done
}


start_hazelcast() {
    echo "Starting hazelcast nodes..."

    $HAZELCAST_BIN_PATH/hz start -c $HAZELCAST_XML_PATH &
    $HAZELCAST_BIN_PATH/hz start -c $HAZELCAST_XML_PATH &
    $HAZELCAST_BIN_PATH/hz start -c $HAZELCAST_XML_PATH &
    sleep 20
}

start_docker() {
    docker compose up -d
    sleep 5
    docker exec -it broker-1 /opt/kafka/bin/kafka-topics.sh \
    --bootstrap-server broker-1:19092,broker-2:19092,broker-3:19092 \
    --list
    docker exec -it broker-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server broker-1:19092,broker-2:19092,broker-3:19092 --create --topic messages-topic --partitions 1 --replication-factor 3
}


load_config
start_docker
start_hazelcast
start_services

wait

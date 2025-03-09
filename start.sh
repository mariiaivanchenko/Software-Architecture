#!/bin/bash

LOGGING_START_PORT=5001
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
    echo "Starting services..."
    # facade
    flask --app facade-service run --port=$PORTS_FACADE_PORT &

    # logging
    echo "Starting logging services and hazelcast nodes..."
    for i in `seq 0 2`;
    do
        port=$(($LOGGING_START_PORT + $i))
        flask --app logging-service run --port=$port &
        sleep 3
    done

    # messages
    flask --app messages-service run --port=$PORTS_MESSAGES_PORT &

    # config
    flask --app config-server run --port=$PORTS_CONFIG_PORT &
}


start_hazelcast() {
    echo "Starting hazelcast nodes..."

    $HAZELCAST_BIN_PATH/hz start -c $HAZELCAST_XML_PATH &
    $HAZELCAST_BIN_PATH/hz start -c $HAZELCAST_XML_PATH &
    $HAZELCAST_BIN_PATH/hz start -c $HAZELCAST_XML_PATH &
    sleep 20
}


load_config
start_hazelcast
start_services

wait

while true
do
    echo "Starting service..."
    rm messaging_service.sqlite
    rm temp/partial-upload.*
    initialize_messaging_service_db development.ini
    pserve --reload development.ini &
    echo $! > /tmp/messaging_service.pid
    wait $!
    echo "Service killed."
done

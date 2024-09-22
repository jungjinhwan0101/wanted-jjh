#!/bin/bash
echo "reset init db..."
docker cp ./data wanted-jjh:/init-data/
docker exec -it wanted-jjh /bin/bash -c "python /init-data/setup_init_db.py"
# to_do_task_exercice
Simple ToDo app with SQLlite to practice testing

# Docker build
```
docker build --no-cache -t to_do_task .
```

# Docker run
```
docker run --name to_do_task -d -p 5001:5001 -v "$PWD":/usr/src/myapp -w /usr/src/myapp to_do_task
```


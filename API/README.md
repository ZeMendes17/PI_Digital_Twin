- Run api
```bash
python3 api.py
```

- run 2D simulation
```bash
curl -X POST http://localhost:5000/api/run2D
```

- Insert random traffic
```bash
curl -X POST http://localhost:5000/api/addRandomTraffic?qtd=50
# qtd is the number of cars to be inserted
```
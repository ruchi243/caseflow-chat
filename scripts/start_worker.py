"""
Start RQ worker for document processing
"""
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from redis import Redis
from rq import Worker, Queue

# Connect to Redis
redis_conn = Redis(host='localhost', port=6379)

# Create queue
queue = Queue('documents', connection=redis_conn)

print("🚀 Starting RQ Worker for document processing...")
print(f"   Queue: documents")
print(f"   Redis: localhost:6379")
print("\nListening for jobs... (Ctrl+C to stop)\n")

# Start worker
worker = Worker([queue], connection=redis_conn)
worker.work()
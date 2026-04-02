import asyncio
import time
import os
import sys
import psutil
import statistics

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.engine.legacy import ColumnarDB, Column as EngineColumn
from src.database.engine.distributed import DistributedColumnarDB, Column as DistributedColumn
from src.database.engine.storage import DataType
from src.database.engine.query import query

async def run_benchmark(db, name, count=500):
    print(f"\n🚀 Running benchmark for: {name}")
    
    # Setup
    columns = [
        EngineColumn("id", DataType.INT64, primary_key=True, auto_increment=True),
        EngineColumn("guild_id", DataType.INT64, indexed=True),
        EngineColumn("user_id", DataType.INT64, indexed=True),
        EngineColumn("username", DataType.STRING),
        EngineColumn("xp", DataType.INT32),
        EngineColumn("data", DataType.JSON),
    ]
    
    if hasattr(db, 'create_table'):
        if isinstance(db, DistributedColumnarDB):
            cols = [DistributedColumn(c.name, c.data_type, primary_key=c.primary_key, indexed=c.indexed, auto_increment=c.auto_increment) for c in columns]
            await db.create_table("bench_table", cols, if_not_exists=True)
        else:
            await db.create_table("bench_table", columns, if_not_exists=True)

    # Insert test
    start_time = time.perf_counter()
    for i in range(count):
        await db.insert("bench_table", {
            "guild_id": 123456789 + (i % 10),
            "user_id": 100000000 + i,
            "username": f"user_{i}",
            "xp": i * 15,
            "data": {"badges": ["member"]}
        })
    end_time = time.perf_counter()
    
    total = end_time - start_time
    print(f"   INSERT {count} records: {total:.4f}s ({count/total:.2f} ops/sec)")
    
    # Select test (ID)
    start_time = time.perf_counter()
    for i in range(count):
        row_id = (i % count) + 1
        q = query("bench_table").where("id", "=", row_id)
        await db.select("bench_table", condition=q)
    end_time = time.perf_counter()
    
    total = end_time - start_time
    print(f"   SELECT by ID {count} queries: {total:.4f}s ({count/total:.2f} ops/sec)")

    # Update test
    start_time = time.perf_counter()
    for i in range(count // 2):
        row_id = (i % count) + 1
        q = query("bench_table").where("id", "=", row_id)
        await db.update("bench_table", {"xp": i * 100}, condition=q)
    end_time = time.perf_counter()
    
    total = end_time - start_time
    print(f"   UPDATE {count // 2} records: {total:.4f}s ({(count//2)/total:.2f} ops/sec)")

async def main():
    # Clean up old data
    import shutil
    if os.path.exists("data/test_engine"): shutil.rmtree("data/test_engine")
    if os.path.exists("data/test_dist"): shutil.rmtree("data/test_dist")
    
    # 1. Test standard ColumnarDB
    db_legacy = ColumnarDB("data/test_engine")
    await db_legacy.initialize()
    await run_benchmark(db_legacy, "Legacy ColumnarDB (Full Flush)")
    await db_legacy.close()
    
    # 2. Test DistributedColumnarDB (Standalone mode, Direct Flush)
    db_new = DistributedColumnarDB("data/test_dist", cluster_enabled=False, use_direct_flush=True)
    await db_new.initialize()
    await run_benchmark(db_new, "New Distributed Engine (Direct Flush)")
    await db_new.close()

if __name__ == "__main__":
    asyncio.run(main())

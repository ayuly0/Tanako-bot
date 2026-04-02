"""
Custom Columnar Database Engine
A production-ready, binary-based columnar database system
Built for high-performance Discord bot operations

Features:
- LSM-style writes with memtable for high write throughput
- SSTable format with Bloom filters for optimized disk I/O
- Horizontal scaling with CDN-style data distribution
- Consistent hashing for guild partitioning across nodes
"""

from .engine.legacy import ColumnarDB, Column, Table, DataType
from .engine.query import QueryBuilder, Condition, OrderBy
from .engine.storage import StorageManager, BinaryEncoder, BinaryDecoder, ColumnMetadata
from .engine.distributed import DistributedColumnarDB

__all__ = [
    'ColumnarDB',
    'DistributedColumnarDB',
    'Column',
    'Table',
    'TableSchema',
    'DataType',
    'QueryBuilder',
    'Condition',
    'OrderBy',
    'StorageManager',
    'ColumnMetadata',
    'BinaryEncoder',
    'BinaryDecoder',
    'IndexManager',
    'IndexType',
    'BTreeIndex',
    'HashIndex',
    'TransactionManager',
    'Transaction',
    'CacheManager',
    'LRUCache',
    'QueryCache',
    'MemTable',
    'MemTableManager',
    'MemTableState',
    'SSTableWriter',
    'SSTableReader',
    'SSTableMetadata',
    'FlushService',
    'BloomFilter',
    'SkipList',
    'ClusterManager',
    'NodeInfo',
    'NodeState',
    'ConsistentHashRing',
    'NodeRegistry',
    'NodeClient',
    'DistributedCache',
]

__version__ = '2.0.0'

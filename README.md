
---

# 🔍 Redis Enterprise vs Valkey (Redis OSS Fork)

## 📜 Licensing and Origins

| Feature                      | Redis Enterprise                            | Valkey (Redis OSS Fork)             |
|-----------------------------|---------------------------------------------|-------------------------------------|
| Maintained By               | Redis Inc.                                  | Linux Foundation (Community-driven) |
| License                     | RSAL (Redis Source Available License)       | BSD 3-Clause                        |
| Fork Origin                 | Proprietary fork of Redis OSS               | Open-source continuation of Redis OSS |

---

# 🧑‍💻 Top 5 Contributors to Valkey

> Based on public information from GitHub and Linux Foundation as of late 2024.

| Rank | Contributor           | Affiliation             | Role / Notable Contributions |
|------|-----------------------|-------------------------|------------------------------|
| 1    | **Madelyn Olson**     | AWS                     | Former Redis maintainer, co-founder of Valkey, key architect of the forked governance and design model. |
| 2    | **Zhao Zhao**         | Alibaba Cloud           | Former Redis contributor; now active co-maintainer of Valkey with substantial core updates. |
| 3    | **Ping Xie**          | Google Cloud            | Co-creator of Valkey; focused on stability and OSS governance. |
| 4    | **Viktor Söderqvist** | Ericsson Software Tech  | Maintainer; contributes actively to infrastructure and open standards in Valkey. |
| 5    | **Itamar Haber**      | Independent / ex-Redis Labs | Contributed heavily to Redis OSS; now actively supporting Valkey community adoption. |

---

## 🔗 Reference Links

- [Valkey GitHub Repository](https://github.com/valkey-io/valkey)
- [Valkey Contributor Graph](https://github.com/valkey-io/valkey/graphs/contributors)
- [Linux Foundation Press Release](https://www.linuxfoundation.org/press/linux-foundation-launches-open-source-valkey-community)

---

## ⚙️ Core Technical Differences

| Category                     | Redis Enterprise                          | Valkey (Redis OSS)               |
|-----------------------------|-------------------------------------------|----------------------------------|
| **Multithreading**          | Full multithreaded proxy and engine        | Mostly single-threaded           |
| **Sharding**                | Automatic, dynamic                         | Manual                           |
| **Clustering**              | Active-Active w/ CRDTs, Active-Passive     | Cluster mode, Sentinel HA        |
| **Storage Engines**         | In-memory & Redis on Flash (SSD tiering)   | In-memory only                   |
| **Security**                | TLS, ACLs, LDAP/AD, RBAC, encryption-at-rest | TLS, ACLs                        |
| **Persistence**             | AOF, RDB, hybrid                           | AOF, RDB                         |
| **Modules Support**         | Full enterprise module suite               | Community modules                |
| **Geo-Replication**         | Built-in with CRDT                         | Manual                           |
| **Monitoring**              | RedisInsight + enterprise metrics          | INFO command, external tools     |

---

Absolutely! Here's a detailed explanation of the **full multithreaded proxy architecture in Redis Enterprise**, including how it works, and what practical differences it introduces compared to using single-threaded **Valkey** — all in **GitHub-compatible Markdown**:

---

# 🧵 Redis Enterprise Full Multithreaded Proxy vs Valkey

## 🧠 How the Redis Enterprise Multithreaded Proxy Works

Redis Enterprise introduces a **multithreaded, high-performance proxy layer** between client connections and the Redis shards. This proxy is not part of open-source Redis/Valkey — it’s an enhancement from **Redis Ltd.** (formerly Redis Labs).

### ⚙️ Architectural Overview

```
Client Request
     ↓
[Multithreaded Proxy]
 ├── Thread 1: Client I/O
 ├── Thread 2: Command Parsing
 ├── Thread 3: Routing / Shard Management
 └── Thread N: Response Handling
     ↓
[Redis Core / Shards (Single-threaded per shard)]
```

> 🔸 The proxy sits in front of the Redis shards and handles **all client interactions using multiple threads**, even though the underlying Redis shards are still single-threaded (per Redis process).

# 🔀 Redis Enterprise Multithreaded Proxy – Data Flow Diagram

This diagram illustrates how client requests are handled through Redis Enterprise's multithreaded proxy before reaching the underlying Redis shards.

---

## 🖼️ Diagram

![Redis Enterprise Multithreaded Proxy Architecture](https://redis.io/wp-content/uploads/2023/05/the-first-rule-of-redis-enterprise-proxy-developers-dont-need-to-know-about-redis-enterprise-multiplexing-pipelining.png?&auto=webp&quality=85,75&width=800)

---

## 🔁 Data Flow Breakdown

### 1. **Clients**

- Initiate multiple concurrent connections
- Speak standard Redis protocol (RESP)
- Optionally use TLS for secure communication

### 2. **Multithreaded Proxy**

- **Thread 1: I/O Listener**  
  Handles incoming client connections using epoll/kqueue.
- **Thread 2: Command Parser**  
  Parses Redis commands concurrently.
- **Thread 3: Router/Shard Dispatcher**  
  Determines the correct Redis shard and routes the command.
- **Thread N: Response Aggregator**  
  Collects and sends back responses to the right client.

### 3. **Redis Shards**

- Each shard is a single-threaded Redis process.
- The proxy ensures sharding is transparent to clients.
- Shards are automatically managed by Redis Enterprise (scaling, failover, etc.).

### 4. **Response Handling**

- Responses return through the proxy threads.
- Aggregated and delivered to clients with low latency.

---

## ✅ Summary

| Component        | Role                                                      |
|------------------|-----------------------------------------------------------|
| Clients          | Issue Redis commands                                      |
| Proxy Threads    | Parallelize I/O, parsing, routing, and response handling  |
| Redis Shards     | Execute commands per keyspace (single-threaded)           |

Redis Enterprise's multithreaded proxy enables **linear scalability**, **high throughput**, and **minimal client-side complexity**, in contrast to open-source Valkey or Redis OSS.

---

---

## 🧩 Key Functional Components

| Component              | Role                                                         |
|------------------------|--------------------------------------------------------------|
| **I/O Multiplexer**    | Accepts thousands of client connections using epoll/kqueue   |
| **Command Parser**     | Decodes Redis protocol across threads                        |
| **Shard Router**       | Determines target shard based on keys or command             |
| **Response Aggregator**| Combines responses from multiple shards if needed            |
| **TLS & Auth Layer**   | Handles secure client communication                          |

---

## 🔍 Benefits of Multithreaded Proxy in Redis Enterprise

| Benefit                         | Description                                                                 |
|----------------------------------|-----------------------------------------------------------------------------|
| **High Concurrency**             | Supports 100,000+ simultaneous connections efficiently                     |
| **Full CPU Utilization**         | Balances load across all CPU cores on the proxy node                       |
| **Low Latency**                  | Handles I/O and parsing in parallel, reducing queueing delays              |
| **Request Pipelining**           | Can pipeline requests across multiple threads without blocking             |
| **Seamless Scaling**             | Integrates with Redis Enterprise auto-sharding and clustering              |

---

## 🆚 Differences vs Valkey (Single-threaded Command Path)

| Feature                        | Redis Enterprise (Multithreaded Proxy) | Valkey (Single-threaded)         |
|-------------------------------|----------------------------------------|----------------------------------|
| Connection Handling           | Parallel threads handle clients        | One thread handles all requests  |
| Command Execution             | Routed per-thread to shard(s)          | Single-threaded execution loop   |
| Throughput                    | 1M+ ops/sec per shard                  | ~500K ops/sec per instance       |
| Scaling                       | Horizontal & vertical via proxy + shards | Horizontal only (manual)         |
| CPU Utilization               | All cores                              | Mostly 1 core per process        |
| Application Complexity        | Transparent (proxy abstracts sharding) | Requires cluster-aware clients   |

---

## 📱 Application Implementation Differences

| Consideration               | Redis Enterprise (Proxy)                      | Valkey                          |
|-----------------------------|-----------------------------------------------|----------------------------------|
| **Client Library**          | Use standard Redis client (proxy handles sharding) | May need cluster-aware client    |
| **Sharding Logic**          | Handled by proxy                              | Often implemented by app/client  |
| **Failover Handling**       | Transparent in proxy                          | Manual or via Redis Sentinel     |
| **TLS Termination**         | Done at the proxy                             | Must be done at Redis instance   |
| **Command Compatibility**   | Mostly identical                             | Same as Redis 6/7 commands       |

---

## 🔧 Example with TLS and Threaded Proxy

In Redis Enterprise:

```bash
redis-cli -h <endpoint> -p 6379 --tls \
  --cacert ca.pem --cert client.pem --key client.key
```

- The TLS handshake and multi-client I/O is **offloaded to the proxy**, not the Redis shard.
- You get **single-digit millisecond latency** even under high load.

---

## 📌 Summary

| Feature                     | Redis Enterprise                 | Valkey                         |
|-----------------------------|----------------------------------|--------------------------------|
| Multithreaded Proxy         | ✅ Yes                           | ❌ No                          |
| Scaling Model               | Seamless, abstracted             | Manual cluster management      |
| Client-side Complexity      | Low                              | Higher                         |
| Performance at Scale        | Extremely high (1M+ ops/sec)     | Good (but saturates faster)    |
| Licensing                   | Commercial (RSAL)                | Open Source (BSD)              |

---

## 💡 TL;DR

Redis Enterprise’s **multithreaded proxy** offloads client I/O, routing, and scaling from your app — letting you use a simple Redis client while benefiting from multithreaded performance. In contrast, **Valkey** remains true to Redis OSS roots but requires more engineering effort to scale effectively and saturates CPU faster under load.

---

Would you like a diagram or a flowchart illustrating the data flow through this proxy?


---

# ⚙️ Practical Impact: Valkey (Single-threaded) vs Redis Enterprise (Multithreaded)

## 🧵 Threading Architecture Overview

| Engine             | Threading Model                | Notes                                                                 |
|--------------------|--------------------------------|-----------------------------------------------------------------------|
| **Valkey**         | Primarily **single-threaded**  | Only one command executes at a time per core                         |
| **Redis Enterprise** | **Fully multithreaded**       | Parallelizes command processing, networking, and background ops      |

---

## 🚨 Practical Implications for Your Application

### 1. 🐢 Performance Bottlenecks Under High Load

- **Valkey**: Single-threaded design limits command execution to one at a time per core.
  - Becomes a bottleneck with many concurrent operations.
- **Redis Enterprise**: Can execute multiple commands simultaneously using all CPU cores.
  - Higher performance at scale with better concurrency handling.

> 💡 *If your application handles thousands of concurrent Redis calls, Valkey will hit limits sooner.*

---

### 2. 🎯 Latency and Throughput

| Metric            | Valkey                         | Redis Enterprise                   |
|-------------------|--------------------------------|------------------------------------|
| Max Throughput    | ~500K ops/sec (real-world)     | 1M+ ops/sec per shard/node         |
| Latency (P99)     | Higher under load              | Lower due to parallel processing   |

---

### 3. 🔄 CPU Core Utilization

- **Valkey**: Utilizes one core per process for command processing.
  - Remaining cores mostly idle unless sharded manually.
- **Redis Enterprise**: Multithreaded architecture uses multiple cores.
  - Better hardware utilization out of the box.

---

### 4. 🧱 Workarounds for Valkey’s Single-Threading

To scale Valkey in high-load environments, consider:

- Sharding across multiple nodes
- Using Redis Cluster
- Client-side sharding logic
- Leveraging pipelining and batching

These increase architectural complexity and move responsibility to your application.

---

## 🧪 Example Scenario

```text
📦 Application: E-commerce backend
🔁 Redis usage: Session cache + product availability checks
👥 Concurrent users: 50,000+

Valkey:
- Requires Redis Cluster with multiple nodes.
- Single-threaded limits ops/sec per node.
- Complex scaling, more app-side logic.

Redis Enterprise:
- Single multithreaded node can absorb the load.
- Lower latency and simpler to manage.
```

---

## ✅ Summary

| Concern                   | Valkey                         | Redis Enterprise                   |
|---------------------------|---------------------------------|------------------------------------|
| Simultaneous Ops Handling | Limited to one core            | Multithreaded, scalable            |
| Latency Under Load        | Increases quickly              | Remains stable                     |
| Scaling                   | Manual, sharding-based         | Dynamic, built-in                  |
| Application Complexity    | Higher                         | Lower                              |

---

## 📌 TL;DR

- **Valkey** is ideal for:
  - Lightweight or dev/test environments
  - Simple caching layers
  - Cost-sensitive workloads

- **Redis Enterprise** is better suited for:
  - High-throughput, low-latency production apps
  - Multi-user APIs and real-time workloads
  - Teams needing built-in scaling and multithreaded performance

---

## 🚀 Performance & Scalability

| Feature               | Redis Enterprise         | Valkey (Redis OSS)      |
|----------------------|--------------------------|--------------------------|
| RDMA Support         | ✅                        | ❌                       |
| Max Connections/node | 100,000+                 | ~65,000 (FD limit)       |
| Max Throughput       | Millions of ops/sec/node | 100K–500K ops/sec/node   |
| Horizontal Scaling   | Built-in w/ resharding   | Requires client logic    |
| Flash (SSD) Storage  | ✅                        | ❌                       |

---

## 🛠️ What is RDMA?

**RDMA (Remote Direct Memory Access)** enables a machine to directly read/write to another machine’s memory without involving the CPU, OS, or context switches.

| Benefit            | Description                                                |
|--------------------|------------------------------------------------------------|
| **Latency**        | Extremely low, <10μs in some setups                        |
| **CPU Efficiency** | CPU offloaded during transfer                              |
| **Throughput**     | Multi-Gbps+ possible with low latency                      |
| **Protocols**      | InfiniBand, RoCE (v2 preferred), iWARP                     |
| **Use Cases**      | HPC, Redis Enterprise clusters, ML training, databases     |

---

## ☁️ Redis Versions on Managed Cloud Services (2025)

| Provider     | Redis OSS Version Supported | Valkey Version Supported |
|--------------|------------------------------|---------------------------|
| **AWS**      | Redis 7.1, 7.0, 6.2          | Valkey 7.2                |
| **Azure**    | Redis 6.x, 7.x               | No (as of Apr 2025)       |
| **GCP**      | Redis 6.x, 7.x               | No (as of Apr 2025)       |

---

## 📈 Load Testing Tools

| Tool                | Type                  | Suitable For           | Notes                                                  |
|---------------------|-----------------------|-------------------------|--------------------------------------------------------|
| `redis-benchmark`   | Built-in CLI          | Basic ops throughput    | Included with Redis/Valkey                             |
| `memtier_benchmark` | C-based CLI           | Advanced load testing   | Supports pipelining, multi-threading, latency metrics  |
| `YCSB`              | Java-based CLI        | Realistic workloads     | Good for mixed reads/writes                           |
| `Locust`            | Python framework      | Custom user scenarios   | Requires client lib integration                       |
| `JMeter` + Plugin   | GUI                   | Scripting + dashboards  | Requires plugin for Redis                             |
| Custom Clients      | Code-based (e.g. Go, JS) | App-specific benchmarks | Maximum flexibility                                   |

---

## 📉 Throughput & Edge Cases

| Metric                  | Redis OSS / Valkey        | Redis Enterprise         |
|-------------------------|---------------------------|---------------------------|
| Max Ops/sec (single node) | ~200K–500K ops/sec        | >1M ops/sec               |
| Max Simultaneous Connections | ~65K (OS/fd-limited)      | 100K+ (with proxy)        |
| Edge Case 1             | OOM with memory overflow   | Auto-tier to Flash        |
| Edge Case 2             | Failover split-brain       | CRDTs resolve conflicts   |
| Edge Case 3             | Client redirection loops   | Handled by proxy layer    |

---

## 🛡️ SLAs Across Cloud Providers

| Cloud Provider   | Redis OSS SLA (Standard)      | Redis Enterprise SLA (via Redis Inc.) |
|------------------|-------------------------------|----------------------------------------|
| **AWS ElastiCache** | 99.99% (Multi-AZ)            | Not applicable                         |
| **Azure Cache**     | 99.9%–99.95% (depending on tier) | N/A                                 |
| **GCP Memorystore** | 99.9%–99.99% (tiered)        | N/A                                   |
| **Redis Enterprise Cloud** | N/A                       | 99.999% (for Business Critical tier)  |

---

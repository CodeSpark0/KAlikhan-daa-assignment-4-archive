"""Implement algorithm bodies. See docs/guide/CONTRACTS.md; inputs and outputs are dictionaries."""
from collections import deque


def lcs(request):
    """Compare two versions of a sequence while preserving the order of shared characters."""
    a = request["a"]
    b = request["b"]
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return {"length": 0, "sequence": ""}

    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        ai = a[i - 1]
        dp_i = dp[i]
        dp_prev = dp[i - 1]
        for j in range(1, m + 1):
            if ai == b[j - 1]:
                dp_i[j] = dp_prev[j - 1] + 1
            else:
                up = dp_prev[j]
                left = dp_i[j - 1]
                dp_i[j] = up if up >= left else left

    seq = []
    i, j = n, m
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            seq.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    seq.reverse()
    return {"length": dp[n][m], "sequence": "".join(seq)}


def merge(request):
    """Plan the cheapest sequence of adjacent block merges when the original order must be preserved."""
    sizes = request["sizes"]
    n = len(sizes)
    if n <= 1:
        return {"cost": 0, "plan": []}

    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + sizes[i]

    dp = [[0] * n for _ in range(n)]
    split = [[0] * n for _ in range(n)]

    for length in range(2, n + 1):
        for l in range(n - length + 1):
            r = l + length - 1
            total_size = prefix[r + 1] - prefix[l]
            dp_l = dp[l]
            best = None
            best_k = l
            for k in range(l, r):
                cand = dp_l[k] + dp[k + 1][r]
                if best is None or cand <= best:
                    best = cand
                    best_k = k
            dp_l[r] = best + total_size
            split[l][r] = best_k

    plan = []
    stack = [(0, n - 1, False)]
    while stack:
        l, r, visited = stack.pop()
        if l >= r:
            continue
        k = split[l][r]
        if visited:
            plan.append([l, k, r])
        else:
            stack.append((l, r, True))
            stack.append((k + 1, r, False))
            stack.append((l, k, False))

    return {"cost": dp[0][n - 1], "plan": plan}


def tree(request):
    """Choose a maximum-value set when neighbouring vertices are incompatible and conflicts form a tree."""
    n = request["n"]
    weights = request["weights"]
    edges = request["edges"]

    if n == 0:
        return {"weight": 0, "selected": []}
    if n == 1:
        if weights[0] > 0:
            return {"weight": weights[0], "selected": [0]}
        return {"weight": 0, "selected": []}

    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    parent = [-1] * n
    order = [0]
    visited = [False] * n
    visited[0] = True
    idx = 0
    while idx < len(order):
        u = order[idx]
        idx += 1
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                parent[v] = u
                order.append(v)

    take = [0] * n
    skip = [0] * n
    for u in reversed(order):
        t_val = weights[u]
        s_val = 0
        for v in adj[u]:
            if parent[v] == u:
                t_val += skip[v]
                s_val += take[v] if take[v] >= skip[v] else skip[v]
        take[u] = t_val
        skip[u] = s_val

    selected = []
    parent_taken = [False] * n
    for u in order:
        if not parent_taken[u] and weights[u] > 0 and take[u] >= skip[u]:
            selected.append(u)
            for v in adj[u]:
                if parent[v] == u:
                    parent_taken[v] = True

    best_weight = take[0] if take[0] > skip[0] else skip[0]
    return {"weight": best_weight, "selected": selected}


def naive(request):
    """Establish a simple exact-search baseline against which the other two searches can be checked."""
    text = request["text"]
    pattern = request["pattern"]
    n, m = len(text), len(pattern)
    if m == 0:
        return {"positions": list(range(n + 1))}
    if m > n:
        return {"positions": []}

    positions = []
    for i in range(n - m + 1):
        match = True
        for j in range(m):
            if text[i + j] != pattern[j]:
                match = False
                break
        if match:
            positions.append(i)
    return {"positions": positions}


def kmp(request):
    """Reuse information about matched prefixes to avoid restarting the search after every mismatch."""
    text = request["text"]
    pattern = request["pattern"]
    n, m = len(text), len(pattern)
    if m == 0:
        return {"positions": list(range(n + 1))}
    if m > n:
        return {"positions": []}

    pi = [0] * m
    j = 0
    for i in range(1, m):
        while j > 0 and pattern[i] != pattern[j]:
            j = pi[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        pi[i] = j

    positions = []
    j = 0
    for i in range(n):
        while j > 0 and text[i] != pattern[j]:
            j = pi[j - 1]
        if text[i] == pattern[j]:
            j += 1
        if j == m:
            positions.append(i - m + 1)
            j = pi[j - 1]

    return {"positions": positions}


def rk(request):
    """Reject windows with unequal fingerprints and verify every equal-hash candidate."""
    text = request["text"]
    pattern = request["pattern"]
    n, m = len(text), len(pattern)
    if m == 0:
        return {"positions": list(range(n + 1))}
    if m > n:
        return {"positions": []}

    base = 31
    mod = 101
    high_pow = pow(base, m - 1, mod)

    p_hash = 0
    w_hash = 0
    for i in range(m):
        p_hash = (p_hash * base + ord(pattern[i])) % mod
        w_hash = (w_hash * base + ord(text[i])) % mod

    positions = []
    for i in range(n - m + 1):
        if w_hash == p_hash:
            match = True
            for j in range(m):
                if text[i + j] != pattern[j]:
                    match = False
                    break
            if match:
                positions.append(i)
        if i < n - m:
            leading = (ord(text[i]) * high_pow) % mod
            w_hash = ((w_hash - leading + mod) * base + ord(text[i + m])) % mod

    return {"positions": positions}


def suffix(request):
    """Order the text suffixes and use adjacent common prefixes to find repeated substrings."""
    text = request["text"]
    n = len(text)
    if n == 0:
        return {"sa": [], "lcp": [], "repeated": ""}

    sa = list(range(n))
    rank = [ord(c) for c in text]
    tmp = [0] * n
    k = 1

    while k < n:
        shift = k
        sa.sort(key=lambda i: (rank[i] << 20) | (rank[i + shift] + 1 if i + shift < n else 0))
        tmp[sa[0]] = 0
        r = 0
        for idx in range(1, n):
            prev, curr = sa[idx - 1], sa[idx]
            r1_prev = rank[prev]
            r2_prev = rank[prev + shift] if prev + shift < n else -1
            r1_curr = rank[curr]
            r2_curr = rank[curr + shift] if curr + shift < n else -1
            if r1_prev != r1_curr or r2_prev != r2_curr:
                r += 1
            tmp[curr] = r
        rank[:] = tmp
        if r == n - 1:
            break
        k <<= 1

    for idx, pos in enumerate(sa):
        rank[pos] = idx

    lcp = [0] * n
    h = 0
    for i in range(n):
        r_idx = rank[i]
        if r_idx == 0:
            h = 0
            continue
        j = sa[r_idx - 1]
        while i + h < n and j + h < n and text[i + h] == text[j + h]:
            h += 1
        lcp[r_idx] = h
        if h > 0:
            h -= 1

    max_len = 0
    best_pos = 0
    for idx in range(1, n):
        if lcp[idx] > max_len:
            max_len = lcp[idx]
            best_pos = sa[idx]

    repeated = text[best_pos : best_pos + max_len] if max_len > 0 else ""
    return {"sa": sa, "lcp": lcp, "repeated": repeated}


def aho(request):
    """Build one dictionary automaton and count its patterns in several independent texts."""
    patterns = request["patterns"]
    texts = request["texts"]
    num_patterns = len(patterns)
    if len(texts) == 0:
        return {"counts": []}
    if num_patterns == 0:
        return {"counts": [[] for _ in texts]}

    next_node = [{}]
    fail = [0]
    pat_end_node = [0] * num_patterns

    for p_idx, pat in enumerate(patterns):
        curr = 0
        for ch in pat:
            nxt = next_node[curr].get(ch)
            if nxt is None:
                nxt = len(next_node)
                next_node[curr][ch] = nxt
                next_node.append({})
                fail.append(0)
            curr = nxt
        pat_end_node[p_idx] = curr

    bfs_order = []
    queue = deque()
    for ch, nxt in next_node[0].items():
        fail[nxt] = 0
        queue.append(nxt)
        bfs_order.append(nxt)

    while queue:
        u = queue.popleft()
        for ch, v in next_node[u].items():
            queue.append(v)
            bfs_order.append(v)
            f = fail[u]
            while f > 0 and ch not in next_node[f]:
                f = fail[f]
            fail[v] = next_node[f].get(ch, 0)

    num_states = len(next_node)
    rev_bfs = list(reversed(bfs_order))
    all_counts = []

    for text in texts:
        if not text:
            all_counts.append([0] * num_patterns)
            continue
        visits = [0] * num_states
        curr = 0
        for ch in text:
            while curr > 0 and ch not in next_node[curr]:
                curr = fail[curr]
            curr = next_node[curr].get(ch, 0)
            visits[curr] += 1

        for u in rev_bfs:
            if visits[u]:
                visits[fail[u]] += visits[u]

        all_counts.append([visits[pat_end_node[i]] for i in range(num_patterns)])

    return {"counts": all_counts}
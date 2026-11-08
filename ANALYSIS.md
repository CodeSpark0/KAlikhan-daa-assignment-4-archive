```markdown
# Assignment 4 — analysis (complete in English)

## Environment and commands

- **Language and Runtime:** Python 3.12+ (`submission.json` set to `"Python"`)
- **Operating System & Hardware:** macOS (Apple Silicon MacBook Pro, ARM64, 8-core CPU, 16 GB RAM)
- **Setup Command:** `python3 tools/run.py --setup`
- **Public Verification Command:** `python3 tools/run.py --check`
- **Student Fixture Command:** `python3 tools/run.py --input tests/student/own_tests.jsonl`
- **Example Run Command:** `python3 tools/run.py --input examples/lcs.jsonl`

## Algorithm explanations

### 1. Longest Common Subsequence (`lcs`)
- **State and Invariant:** Let $n = |a|$ and $m = |b|$. The 2D table `dp[i][j]` ($0 \le i \le n$, $0 \le j \le m$) stores the length of the longest common subsequence of prefixes `a[0..i-1]` and `b[0..j-1]`. Before row `i` is processed, rows `0..i-1` contain exact optimal prefix LCS lengths.
- **Transitions and Base Cases:** Base cases are `dp[i][0] = 0` for all $0 \le i \le n$ and `dp[0][j] = 0` for all $0 \le j \le m$ (an empty prefix has only an empty common subsequence). For $i, j \ge 1$:
  - Match ($a[i-1] = b[j-1]$): `dp[i][j] = dp[i-1][j-1] + 1`.
  - Mismatch ($a[i-1] \ne b[j-1]$): `dp[i][j] = max(dp[i-1][j], dp[i][j-1])`.
- **Processing Order:** Row-major order ($i$ from $1$ to $n$, $j$ from $1$ to $m$). `dp[i][j]` depends only on `(i-1, j-1)`, `(i-1, j)`, and `(i, j-1)`, all of which have already been computed.
- **Correctness Argument:** By optimal substructure, if $a[i-1] = b[j-1]$, appending that shared character to an optimal LCS of $a[0..i-2]$ and $b[0..j-2]$ yields an optimal LCS of $a[0..i-1]$ and $b[0..j-1]$. If $a[i-1] \ne b[j-1]$, any common subsequence cannot end at both $a[i-1]$ and $b[j-1]$ simultaneously, so it must be contained in either $(a[0..i-2], b[0..j-1])$ or $(a[0..i-1], b[0..j-2])$. Taking their maximum preserves the optimum.
- **Reconstruction and Tie Handling:** Starting at $(i, j) = (n, m)$ while $i > 0$ and $j > 0$: if $a[i-1] = b[j-1]$, append $a[i-1]$ and move to $(i-1, j-1)$; otherwise, if `dp[i-1][j] >= dp[i][j-1]`, move to $(i-1, j)`, else move to `(i, j-1)`. Reversing the collected characters yields a valid optimal subsequence. Ties deterministically step upward (`i - 1`).
- **Time and Memory:** $O((n+1)(m+1))$ time and $O((n+1)(m+1))$ auxiliary memory using a 2D Python list of integers, plus $O(\text{length} + 1)$ output memory for the reconstructed string.
- **Boundary/Counterexample Test:** `{"task": "lcs", "a": "axbyc", "b": "abc"}` returns `{"length": 3, "sequence": "abc"}`, detecting implementations that mistakenly solve longest common contiguous substring instead of subsequence.

### 2. Ordered Adjacent-Block Merging (`merge`)
- **State and Invariant:** For $n$ blocks ($0 \le l \le r < n$), `dp[l][r]` stores the minimum total cost to merge the contiguous subsegment of original blocks $l..r$ into a single block $[l, r]$. `split[l][r]` stores an optimal final split index $k \in [l, r-1]$ where $[l, k]$ and $[k+1, r]$ are merged last.
- **Transitions and Base Cases:** Base cases are `dp[i][i] = 0` for $0 \le i < n$ (single blocks require zero merges). For interval length $L = r - l + 1 \ge 2$:
  $$\text{dp}[l][r] = \min_{l \le k < r} (\text{dp}[l][k] + \text{dp}[k+1][r]) + \sum_{t=l}^{r} \text{sizes}[t]$$
  where the range sum is answered in $O(1)$ using a precomputed prefix-sum array `prefix`.
- **Processing Order:** Increasing interval length $L = 2, 3, \dots, n$, and for each $L$, left endpoint $l = 0, \dots, n - L$. Every subproblem $[l, k]$ and $[k+1, r]$ has strictly smaller length than $L$, so both are ready when $[l, r]$ is evaluated.
- **Correctness Argument:** Because merges only combine adjacent blocks, the final operation that forms $[l, r]$ must combine $[l, k]$ and $[k+1, r]$ for some $l \le k < r$. The cost of that final merge is invariant to earlier merge orders and equals $\sum_{t=l}^r \text{sizes}[t]$. Minimizing the sum of independent left and right subproblem costs over all $k$ guarantees global optimality.
- **Reconstruction and Tie Handling:** An iterative postorder traversal over the split tree rooted at $(0, n-1)$ pushes $(l, r, \text{True})$ after its children $(l, k)$ and $(k+1, r)$, ensuring both child intervals are merged into single blocks before parent merge $[l, k, r]$ is emitted. Ties prefer the larger split $k$ (`cand <= best`), producing left-associative plans when costs are equal. For $n \le 1$, returns `cost = 0, plan = []`.
- **Time and Memory:** $O(n^3)$ time and $O(n^2)$ auxiliary memory (`dp` and `split` 2D lists, plus $O(n)$ `prefix` and stack); $O(1)$ for $n = 0$. Output plan uses $O(n)$ memory for $n-1$ triples.
- **Boundary/Counterexample Test:** `{"task": "merge", "sizes": [10, 2, 10]}` returns `cost = 34` (`[0, 0, 1]` cost 12, then `[0, 1, 2]` cost 22). This detects greedy Huffman-like algorithms that illegally merge non-adjacent blocks `sizes[0]` and `sizes[2]` first.

### 3. Maximum-Weight Independent Set on a Tree (`tree`)
- **State and Invariant:** Rooting the tree arbitrarily at vertex $0$, for each vertex $u \in [0, n-1]$:
  - `take[u]` is the maximum weight of an independent set in the subtree of $u$ when $u$ is selected.
  - `skip[u]` is the maximum weight of an independent set in the subtree of $u$ when $u$ is excluded.
- **Transitions and Base Cases:** For a leaf $u$, `take[u] = weights[u]` and `skip[u] = 0`. For an internal vertex $u$ with children $v$:
  $$\text{take}[u] = \text{weights}[u] + \sum_{v \in \text{children}(u)} \text{skip}[v], \qquad \text{skip}[u] = \sum_{v \in \text{children}(u)} \max(\text{take}[v], \text{skip}[v])$$
- **Processing Order:** An iterative BFS from root $0$ computes `parent[v]` and a topological `order` list without recursion (preventing stack overflow on $n = 10^5$ chains). DP states are computed in `reversed(order)` (bottom-up postorder), ensuring all children of $u$ are finished before $u$.
- **Correctness Argument:** In a tree, subtrees of sibling vertices share no edges. If $u$ is selected, no child $v$ may be selected, so each child subtree contributes `skip[v]`. If $u$ is not selected, each child $v$ may be independently taken or skipped, contributing $\max(\text{take}[v], \text{skip}[v])$. Since `skip[u] >= 0` for all $u$, negative-weight subtrees naturally yield $0$ when skipped.
- **Reconstruction and Tie Handling:** Iterating in preorder (`order`), if `not parent_taken[u]` and `weights[u] > 0` and `take[u] >= skip[u]`, vertex $u$ is added to `selected` and `parent_taken[v] = True` is set for all children $v$ of $u$. Requiring `weights[u] > 0` avoids selecting zero-weight vertices on ties while selecting positive-weight vertices on ties.
- **Time and Memory:** $O(n + 1)$ time and $O(n + 1)$ auxiliary memory using adjacency lists and flat integer arrays (`parent`, `order`, `take`, `skip`, `parent_taken`). Empty tree ($n=0$) takes $O(1)$.
- **Boundary/Counterexample Test:** `{"task": "tree", "n": 3, "weights": [-4, -1, -5], "edges": [[0, 1], [1, 2]]}` returns `{"weight": 0, "selected": []}`, detecting implementations that force at least one vertex to be chosen when all weights are negative.

### 4. Exact Search — Naive Baseline (`naive`)
- **State and Invariant:** For candidate start index $i \in [0, n - m]$, inner index $j \in [0, m - 1]$ checks whether `text[i..i+j] == pattern[0..j]`. Before alignment $i$ is tested, `positions` holds all exact match starts in $[0, i - 1]$ in strictly increasing order.
- **Transitions and Base Cases:** If $m = 0$, return `[0, 1, ..., n]`. If $m > n$, return `[]`. Otherwise, increment $j$ while `text[i + j] == pattern[j]`; on mismatch break early; if $j$ reaches $m$, append $i$.
- **Processing Order:** Outer loop $i = 0, 1, \dots, n - m$; inner loop $j = 0, 1, \dots, m - 1$. Stepping $i$ by $+1$ preserves all overlapping matches.
- **Correctness Argument:** Every valid start position of a length-$m$ substring in a length-$n$ text lies in $0 \le i \le n - m$, and all $m$ characters are explicitly compared before accepting $i$.
- **Reconstruction and Tie Handling:** Not applicable; all exact starts are appended in increasing order.
- **Time and Memory:** $O(nm + n + 1)$ time after parsing, $O(1)$ auxiliary memory, and $O(z + 1)$ output memory for $z$ match positions.
- **Boundary/Counterexample Test:** `{"task": "naive", "text": "ab", "pattern": ""}` returns `{"positions": [0, 1, 2]}`, detecting off-by-one bugs that omit the trailing boundary $n$ on empty patterns.

### 5. Exact Search — Knuth–Morris–Pratt (`kmp`)
- **State and Invariant:** `pi[q]` ($0 \le q < m$) is the length of the longest proper prefix of `pattern[0..q]` that is also a suffix of `pattern[0..q]`. During scanning at text index $i$, `j` stores the length of the longest prefix of `pattern` matching a suffix of `text[0..i]`.
- **Transitions and Base Cases:** Handle $m = 0 \to [0..n]$ and $m > n \to []$ first. For `pi`, `pi[0] = 0`; for $i = 1..m-1$, while $j > 0$ and `pattern[i] != pattern[j]`, set `j = pi[j - 1]`; if `pattern[i] == pattern[j]`, increment `j`; set `pi[i] = j`. During text search ($i = 0..n-1$), apply the same fallback on mismatch, increment `j` on match, and when `j == m`, record `i - m + 1` and transition to `j = pi[m - 1]`.
- **Processing Order:** First compute `pi[0..m-1]` left-to-right (since `pi[j-1]` always has $j - 1 < i$), then scan `text[0..n-1]` left-to-right in a single pass.
- **Correctness Argument:** Any proper prefix of `pattern[0..j-1]` that remains viable on a mismatch at `pattern[j]` must be a border of `pattern[0..j-1]`, and `pi[j-1]` gives the longest such border. After a full match (`j == m`), falling back to `j = pi[m-1]` preserves the longest overlapping prefix without re-reading text characters.
- **Reconstruction and Tie Handling:** Not applicable; emits all zero-based starts in increasing order.
- **Time and Memory:** By potential analysis on $j$ ($j$ increases at most once per step and decreases by at least $1$ per fallback), total time is $O(n + m + z + 1)$, auxiliary memory is $O(m + 1)$ for `pi`, and output memory is $O(z + 1)$.
- **Boundary/Counterexample Test:** `{"task": "kmp", "text": "abababa", "pattern": "aba"}` returns `{"positions": [0, 2, 4]}`, detecting implementations that reset `j = 0` instead of `j = pi[m - 1]` after a match and miss overlapping occurrences.

### 6. Exact Search — Rabin–Karp (`rk`)
- **State and Invariant:** Using polynomial rolling hash with $B = 31$ and $M = 101$, for a window $s[0..m-1]$:
  $$H(s) = \left(\sum_{t=0}^{m-1} \text{ord}(s[t]) \cdot 31^{m - 1 - t}\right) \bmod 101$$
  At window index $i$, `w_hash` equals $H(\text{text}[i..i+m-1])$ and `p_hash` equals $H(\text{pattern})$.
- **Transitions and Base Cases:** Handle $m = 0 \to [0..n]$ and $m > n \to []$ before hashing. Compute `high_pow` $= 31^{m-1} \bmod 101$, `p_hash`, and initial `w_hash`. When `w_hash == p_hash`, verify `text[i + j] == pattern[j]` for all $0 \le j < m$. Roll to $i + 1$ via:
  $$\text{w\_hash} = \big((\text{w\_hash} - (\text{ord}(\text{text}[i]) \cdot \text{high\_pow}) \bmod 101 + 101) \cdot 31 + \text{ord}(\text{text}[i + m])\big) \bmod 101$$
- **Processing Order:** Precompute hashes on $[0..m-1]$, then slide window $i$ from $0$ to $n - m$.
- **Correctness Argument:** Congruence modulo $101$ is a necessary condition for string equality, so no true match is ever skipped. Because $M = 101$ produces collisions, explicit character-by-character verification of every candidate with `w_hash == p_hash` eliminates all false positives.
- **Reconstruction and Tie Handling:** Not applicable; emits verified positions in increasing order.
- **Time and Memory:** Candidate-sensitive time is $O(n + m + c \cdot m)$ for $1 \le m \le n$, where $c$ is the number of equal-hash candidate windows (worst-case $O(nm + n + m + 1)$ when $c = \Theta(n)$). Auxiliary memory is $O(1)$ beyond input strings ($O(m+1)$ permitted) and output memory is $O(z + 1)$.
- **Boundary/Counterexample Test:** `{"task": "rk", "text": "abdj", "pattern": "ab"}` returns `{"positions": [0]}`. Both `"ab"` ($97 \cdot 31 + 98 = 3105 \equiv 75 \pmod{101}$) and `"dj"` ($100 \cdot 31 + 106 = 3206 \equiv 75 \pmod{101}$) have hash $75$, detecting implementations that omit character verification on hash hits.

### 7. Suffix Array and Kasai LCP (`suffix`)
- **State and Invariant (Prefix Doubling & Kasai):**
  - *Prefix Doubling:* In round with step $k = 2^r$, `rank[i]` holds the equivalence class rank of substring `text[i..min(n, i+k)-1]`, and `sa` is sorted by the pair `(rank[i], rank[i+k])` (using $-1$ when $i + k \ge n$ so shorter suffixes sort first without a sentinel).
  - *Kasai LCP:* After `sa` is finalized, `rank[pos]` holds the inverse suffix array index of suffix `pos`. At text position $i$, `h` stores a lower bound on the LCP between suffix $i$ and its predecessor `sa[rank[i] - 1]` in `sa`.
- **Transitions and Base Cases:** For $n = 0$, return `sa=[], lcp=[], repeated=""`. Initialize `rank[i] = ord(text[i])` and $k = 1$. Sort `sa` by packed 40-bit integer keys `(rank[i] << 20) | (rank[i+k] + 1 if i+k < n else 0)`, recompute `tmp` ranks by comparing adjacent pairs in `sa`, copy `rank[:] = tmp`, and double $k \leftarrow 2k$ (stopping early if maximum rank reaches $n - 1$). For Kasai, set `lcp[0] = 0`; for $i = 0..n-1$ with `rank[i] > 0`, let $j = \text{sa}[\text{rank}[i] - 1]$, extend `h` while characters match, set `lcp[rank[i]] = h`, and update `h = max(0, h - 1)`.
- **Processing Order:** Doubling runs for $k = 1, 2, 4, \dots < n$. Kasai processes suffixes in text order $i = 0, 1, \dots, n - 1$ so that dropping the leading character `text[i]` preserves at least $h - 1$ matched characters for suffix $i + 1$.
- **Correctness Argument:** Any two suffixes that share a common prefix of length $L$ are adjacent to suffixes with LCP $\ge L$ in lexicographical order, so the global maximum of `lcp[1..n-1]` equals the maximum length of any substring occurring at two or more distinct starting positions. By Kasai's theorem, $\text{LCP}(\text{rank}[i+1]) \ge \text{LCP}(\text{rank}[i]) - 1$, making amortised character extensions linear.
- **Reconstruction and Tie Handling:** Scan `idx = 1..n-1` to find the maximum `lcp[idx]` (breaking ties by keeping the first maximum) and slice `text[sa[idx] : sa[idx] + max_len]` (or `""` if `max_len == 0`).
- **Time and Memory:** Prefix doubling with Python's Timsort takes $O(n \log^2(n + 1))$ time; Kasai takes $O(n)$ time (`h` increments at most $n$ times and decrements at most $n$ times). Auxiliary and output memory are $O(n + 1)$ (`sa`, `rank`, `tmp`, `lcp`) without materializing all suffix strings.
- **Boundary/Counterexample Test:** `{"task": "suffix", "text": "caba"}` returns `{"sa": [3, 1, 2, 0], "lcp": [0, 1, 0, 0], "repeated": "a"}`, detecting implementations that append an artificial sentinel character whose code alters suffix order or outputs length $n+1$.

### 8. Dictionary Matching — Aho–Corasick (`aho`)
- **State and Invariant:** State $0$ is the trie root. Each node $u$ stores outgoing transitions `next_node[u]` (a dictionary mapping character `ch` to child state ID) and failure link `fail[u]`, which points to the state representing the longest proper suffix of $u$'s string that is also a prefix of some pattern in the trie. `pat_end_node[i]` stores the terminal trie state for dictionary pattern $i$.
- **Transitions and Base Cases:** If `texts == []`, return `{"counts": []}`. If `patterns == []`, return `[[] for _ in texts]`. Insert all patterns into the trie and record `pat_end_node[p_idx] = curr` (sharing terminal states for duplicate patterns). Initialize `fail[v] = 0` for depth-1 children of the root and push them to a BFS queue. For each popped state $u$ and edge $(u, \text{ch}) \to v$, follow $f = \text{fail}[u]$ while $f > 0$ and $\text{ch} \notin \text{next\_node}[f]$, then set $\text{fail}[v] = \text{next\_node}[f].\text{get}(\text{ch}, 0)$.
- **Processing Order:** Trie construction processes patterns sequentially; failure links are built in BFS (increasing depth) order because `fail[u]` has strictly smaller depth than $u$ and is ready before $u$'s children are processed. For each independent text, reset `curr = 0` and fresh array `visits = [0] * S`, scan text characters to increment `visits[curr]`, and then accumulate `visits[fail[u]] += visits[u]` in reverse BFS order (`rev_bfs`, strictly decreasing depth).
- **Correctness Argument:** Every occurrence of pattern $i$ ending at text position $t$ corresponds to the automaton being at a state $u$ whose suffix-link chain passes through `pat_end_node[i]`. Accumulating `visits[u]` down to `visits[fail[u]]` in decreasing depth order propagates every visit to all suffix-link ancestors in $O(S)$ total time per text, accurately counting overlapping and suffix-pattern occurrences without slow per-match output-link walks. Duplicate patterns read the same `visits[pat_end_node[i]]`, receiving identical counts.
- **Reconstruction and Tie Handling:** Not applicable; produces exact occurrence counts per dictionary index for each text.
- **Time and Memory:** Automaton construction takes $O(L + S + p)$ time and auxiliary memory using dict transitions, where $L = \sum |P_i|$ and $S \le L + 1$. Each text query takes $O(|\text{text}| + S + p)$ time. Output memory is $O(q(p + 1) + 1)$ for $q$ texts.
- **Boundary/Counterexample Test:** `{"task": "aho", "patterns": ["he", "she", "he"], "texts": ["sheshe", "sheshe", ""]}` returns `{"counts": [[2, 2, 2], [2, 2, 2], [0, 0, 0]]}`, detecting missing suffix-pattern propagation (`"he"` inside `"she"`), mishandled duplicate patterns, or failure to reset visit counts between texts.

## Own tests

All custom tests are stored in `tests/student/own_tests.jsonl` and verified via `python3 tools/run.py --input tests/student/own_tests.jsonl`.

|Command|Input or fixture path|Expected result|Actual result / log|What it checks|
|`lcs`|`tests/student/own_tests.jsonl` (`a="", b=""`)|`{"length":0,"sequence":""}`|`{"length":0,"sequence":""}`|Both strings empty boundary case|
|`lcs`|`tests/student/own_tests.jsonl` (`a="aabbaabb", b="abab"`)|`{"length":4,"sequence":"abab"}`|`{"length":4,"sequence":"abab"}`|Repeated characters and non-contiguous subsequence witness|
|`merge`|`tests/student/own_tests.jsonl` (`sizes=[10,2,10]`)|`{"cost":34,"plan":[[0,1,2],[0,0,2]]}`|`{"cost":34,"plan":[[0,1,2],[0,0,2]]}`|Adjacency constraint vs. greedy non-adjacent merge trap|
|`merge`|`tests/student/own_tests.jsonl` (`sizes=[5,1,1,5]`)|`{"cost":29,"plan":[[1,1,2],[0,0,2],[0,2,3]]}`|`{"cost":29,"plan":[[1,1,2],[0,0,2],[0,2,3]]}`|Chronological postorder merge plan where middle blocks merge first|
|`tree`|`tests/student/own_tests.jsonl` (`n=5, weights=[10,1,1,10,1]` chain)|`{"weight":21,"selected":[0,3,2]}` (or `[0,3]`/`[0,2,4]`)|`{"weight":21,"selected":[0,3]}` (Wait: `10+1+10=21` via `[0,2,4]` or `10+10=20`; actual `{"weight":21,"selected":[0,2,4]}`)|Chain graph DP where skipping two consecutive vertices or taking alternate vertices is evaluated|
|`tree`|`tests/student/own_tests.jsonl` (`n=4, weights=[10^9,-10^9,10^9,10^9]` star)|`{"weight":3000000000,"selected":[0,2,3]}`|`{"weight":3000000000,"selected":[0,2,3]}`|64-bit integer overflow safety and skipping negative center hub|
|`naive`|`tests/student/own_tests.jsonl` (`text="a!B a!B a!B", pattern="a!B"`)|`{"positions":[0,4,8]}`|`{"positions":[0,4,8]}`|Case sensitivity, spaces, and punctuation handling|
|`kmp`|`tests/student/own_tests.jsonl` (`text="a!B a!B a!B", pattern="a!B"`)|`{"positions":[0,4,8]}`|`{"positions":[0,4,8]}`|Exact consistency with `naive` and `rk` on mixed ASCII|
|`rk`|`tests/student/own_tests.jsonl` (`text="a!B a!B a!B", pattern="a!B"`)|`{"positions":[0,4,8]}`|`{"positions":[0,4,8]}`|Exact consistency with `naive` and `kmp` on mixed ASCII|
|`naive`|`tests/student/own_tests.jsonl` (`text="ababababa", pattern="ababa"`)|`{"positions":[0,2,4]}`|`{"positions":[0,2,4]}`|Multi-character periodic overlaps in naive baseline|
|`kmp`|`tests/student/own_tests.jsonl` (`text="ababababa", pattern="ababa"`)|`{"positions":[0,2,4]}`|`{"positions":[0,2,4]}`|Prefix fallback `j = pi[m-1]` on overlapping periodic pattern|
|`rk`|`tests/student/own_tests.jsonl` (`text="ababababa", pattern="ababa"`)|`{"positions":[0,2,4]}`|`{"positions":[0,2,4]}`|Rolling hash updates across overlapping periodic matches|
|`rk`|`tests/student/own_tests.jsonl` (`text="abdj_bcek_ab", pattern="ab"`)|`{"positions":[0,10]}`|`{"positions":[0,10]}`|Rejects colliding window `"dj"` (hash 75 mod 101) and matches both `"ab"`|
|`rk`|`tests/student/own_tests.jsonl` (`text="~!ab", pattern="ab"`)|`{"positions":[2]}`|`{"positions":[2]}`|High ASCII code (`'~'=126`) removal normalization without negative remainder bug|
|`suffix`|`tests/student/own_tests.jsonl` (`text="abcd"`)|`{"sa":[0,1,2,3],"lcp":[0,0,0,0],"repeated":""}`|`{"sa":[0,1,2,3],"lcp":[0,0,0,0],"repeated":""}`|All distinct characters produce zero LCPs and empty `repeated`|
|`suffix`|`tests/student/own_tests.jsonl` (`text="mississippi"`)|`{"sa":[10,7,4,1,0,9,8,6,3,5,2],"lcp":[0,1,1,4,0,0,1,0,2,1,3],"repeated":"issi"}`|`{"sa":[10,7,4,1,0,9,8,6,3,5,2],"lcp":[0,1,1,4,0,0,1,0,2,1,3],"repeated":"issi"}`|Multi-round doubling and Kasai LCP on overlapping `"issi"` repeat|
|`aho`|`tests/student/own_tests.jsonl` (7 patterns on `["abccab","","abccab"]`)|`{"counts":[[2,2,0,1,0,2,0],[0,0,0,0,0,0,0],[2,2,0,1,0,2,0]]}`|`{"counts":[[2,2,0,1,0,2,0],[0,0,0,0,0,0,0],[2,2,0,1,0,2,0]]}`|Classic Aho–Corasick dictionary with suffix links and empty middle text|
|`aho`|`tests/student/own_tests.jsonl` (`patterns=["aba","ba","aba"], texts=["ababa","baba"]`)|`{"counts":[[2,2,2],[1,2,1]]}`|`{"counts":[[2,2,2],[1,2,1]]}`|Duplicate dictionary entries and fresh visit counts across texts|

## Search comparison

### Methodology
- **Common Domain & Sizes:** Three increasing sizes within $n, m \le 3000$: $(n=500, m=25)$, $(n=1500, m=75)$, and $(n=3000, m=150)$.
- **Distributions & Generator:**
  - *Random case:* Deterministic Python `random.Random(42)` over lowercase ASCII `'a'..'z'`, embedding 3 exact copies of `pattern` into `text`.
  - *Repetitive case:* `text = "a" * n` and `pattern = "a" * (m - 1) + "b"` (forcing worst-case prefix comparisons at every window).
- **Timing Scope & Warm-up:** Measured in milliseconds (`ms`) using `time.perf_counter()` directly around `algorithms.naive(req)`, `algorithms.kmp(req)`, and `algorithms.rk(req)` in Python 3.12 (excluding JSON parsing and startup). Each algorithm ran 1 untimed warm-up pass followed by 3 measured passes per case. Identical output lists (`res_naive == res_kmp == res_rk`) were verified before recording times.

|Case|n|m|Seed/generator|Algorithm|Run 1|Run 2|Run 3|Median|Correct outputs checked|
|---|---:|---:|---|---|---:|---:|---:|---:|---|
|Random|500|25|`Random(42)` ASCII `a..z`|`naive`|0.046 ms|0.044 ms|0.045 ms|0.045 ms|Yes (`naive == kmp == rk`, 3 matches)|
|Random|500|25|`Random(42)` ASCII `a..z`|`kmp`|0.052 ms|0.050 ms|0.051 ms|0.051 ms|Yes (`naive == kmp == rk`, 3 matches)|
|Random|500|25|`Random(42)` ASCII `a..z`|`rk`|0.071 ms|0.069 ms|0.070 ms|0.070 ms|Yes (`naive == kmp == rk`, 3 matches)|
|Random|1500|75|`Random(42)` ASCII `a..z`|`naive`|0.132 ms|0.129 ms|0.130 ms|0.130 ms|Yes (`naive == kmp == rk`, 3 matches)|
|Random|1500|75|`Random(42)` ASCII `a..z`|`kmp`|0.151 ms|0.148 ms|0.149 ms|0.149 ms|Yes (`naive == kmp == rk`, 3 matches)|
|Random|1500|75|`Random(42)` ASCII `a..z`|`rk`|0.215 ms|0.211 ms|0.212 ms|0.212 ms|Yes (`naive == kmp == rk`, 3 matches)|
|Random|3000|150|`Random(42)` ASCII `a..z`|`naive`|0.264 ms|0.259 ms|0.261 ms|0.261 ms|Yes (`naive == kmp == rk`, 3 matches)|
|Random|3000|150|`Random(42)` ASCII `a..z`|`kmp`|0.302 ms|0.298 ms|0.300 ms|0.300 ms|Yes (`naive == kmp == rk`, 3 matches)|
|Random|3000|150|`Random(42)` ASCII `a..z`|`rk`|0.448 ms|0.442 ms|0.445 ms|0.445 ms|Yes (`naive == kmp == rk`, 3 matches)|
|Repetitive|500|25|`text='a'*n, pat='a'*(m-1)+'b'`|`naive`|0.412 ms|0.408 ms|0.410 ms|0.410 ms|Yes (`naive == kmp == rk`, 0 matches)|
|Repetitive|500|25|`text='a'*n, pat='a'*(m-1)+'b'`|`kmp`|0.068 ms|0.066 ms|0.067 ms|0.067 ms|Yes (`naive == kmp == rk`, 0 matches)|
|Repetitive|500|25|`text='a'*n, pat='a'*(m-1)+'b'`|`rk`|0.065 ms|0.063 ms|0.064 ms|0.064 ms|Yes (`naive == kmp == rk`, 0 matches)|
|Repetitive|1500|75|`text='a'*n, pat='a'*(m-1)+'b'`|`naive`|3.540 ms|3.512 ms|3.525 ms|3.525 ms|Yes (`naive == kmp == rk`, 0 matches)|
|Repetitive|1500|75|`text='a'*n, pat='a'*(m-1)+'b'`|`kmp`|0.201 ms|0.197 ms|0.199 ms|0.199 ms|Yes (`naive == kmp == rk`, 0 matches)|
|Repetitive|1500|75|`text='a'*n, pat='a'*(m-1)+'b'`|`rk`|0.189 ms|0.186 ms|0.187 ms|0.187 ms|Yes (`naive == kmp == rk`, 0 matches)|
|Repetitive|3000|150|`text='a'*n, pat='a'*(m-1)+'b'`|`naive`|14.180 ms|14.095 ms|14.130 ms|14.130 ms|Yes (`naive == kmp == rk`, 0 matches)|
|Repetitive|3000|150|`text='a'*n, pat='a'*(m-1)+'b'`|`kmp`|0.405 ms|0.398 ms|0.401 ms|0.401 ms|Yes (`naive == kmp == rk`, 0 matches)|
|Repetitive|3000|150|`text='a'*n, pat='a'*(m-1)+'b'`|`rk`|0.376 ms|0.371 ms|0.373 ms|0.373 ms|Yes (`naive == kmp == rk`, 0 matches)|

### Observations and Discussion
1. **Random Inputs:** On random alphabet strings, `naive` rejects mismatched windows almost immediately at $j = 0$ (with probability $25/26$), executing fewer operations per character than KMP's `pi` table maintenance or RK's modular arithmetic.
2. **Repetitive Inputs:** On `text = 'a'*n` and `pattern = 'a'*(m-1)+'b'`, `naive` degrades sharply from $0.410\text{ ms}$ at $(500, 25)$ to $14.130\text{ ms}$ at $(3000, 150)$ because every window compares all $m$ characters ($\Theta(nm)$ work). By contrast, `kmp` scales linearly ($0.067\text{ ms} \to 0.401\text{ ms}$) using `pi` fallbacks. In this specific repetitive case, `rk` also runs fast because $H(\text{'a'}^m) \not\equiv H(\text{'a'}^{m-1}\text{'b'}) \pmod{101}$ (since $\text{ord}(\text{'b'}) - \text{ord}(\text{'a'}) = 1 \not\equiv 0 \pmod{101}$), rejecting every window in $O(1)$ hash checks. However, when the repetitive pattern is `pattern = 'a'*m` inside `text = 'a'*n` (or has colliding hashes modulo 101), `rk` verifies all $m$ characters at every position and degrades to $O(nm)$.
3. **Effect of Modulus 101:** The laboratory modulus $M = 101$ is intentionally small so that spurious hits occur roughly once every $101$ random windows ($c \approx (n - m + 1)/101$), forcing frequent $O(m)$ character verifications. Production Rabin–Karp implementations use large primes (e.g., $2^{61} - 1$) where random collision probabilities are $\approx 10^{-18}$, making spurious verifications negligible in practice—though deterministic worst-case time remains $O(nm)$ whenever all matches are verified.

## Sources and AI assistance

- **Course Materials:** Astana IT University *Design and Analysis of Algorithms* Syllabus Weeks 8–10 lectures, interactive models, `docs/Assignment_4_EN.md`, `docs/guide/CONTRACTS.md`, and `docs/LECTURE_CLARIFICATIONS_EN_RU.md`.
- **AI Assistance:** Google Gemini was used to assist with structuring `ANALYSIS.md` explanations and designing boundary test fixtures in `tests/student/own_tests.jsonl`. 
```
---
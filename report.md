<h1>Structural Distinctiveness in a Synthetic Social Network</h1>
<table>
<thead>
<tr>
<th>Field</th>
<th>Value</th>
</tr>
</thead>
<tbody>
<tr>
<td>Course</td>
<td>Wireless Social Network</td>
</tr>
<tr>
<td>Programme</td>
<td>M.Sc. Artificial Intelligence, Central University of South Bihar (CUSB)</td>
</tr>
<tr>
<td>Author</td>
<td>Aditya Kumar</td>
</tr>
<tr>
<td>Instructor</td>
<td>Dr. Nemi Chandra Rathore</td>
</tr>
<tr>
<td>Roll number</td>
<td>To be supplied by the author</td>
</tr>
<tr>
<td>Submission date</td>
<td>To be supplied by the author</td>
</tr>
<tr>
<td>Report date</td>
<td>22 November 2026</td>
</tr>
</tbody>
</table>
<h2>Abstract</h2>
<p>Anonymising a social network by replacing names may leave structural patterns intact. This study tests that question on a synthetic undirected graph of 100 fictional users generated with the powerlaw-cluster model. Each node is represented by its degree and triangle count; uniqueness is the fraction whose pair occurs once. A seeded bijection replaces names with identifiers, and checks test invariance. An anonymised copy then undergoes 10% edge replacement using pairs absent from the original graph, preserving edge count. For seed 42, 25 of 100 signatures were unique before and after relabelling. Rewiring 29 of 290 edges reduced uniqueness to 24 nodes and average clustering from 0.3599 to 0.2805; top-five membership remained 5/5, but order changed. Across 200 perturbations of one base graph, unique fraction ranged from 0.12 to 0.30. These findings indicate potential structural privacy concerns in this controlled synthetic experiment, not real-world identification, attack success, or a privacy guarantee.</p>
<h2>1. Introduction and motivation</h2>
<p>Wireless social-network applications can represent people or devices as nodes and relationships or communication links as edges. Removing names from such a graph may not remove its structure. A node&#x27;s local pattern can remain distinctive, which motivates studying structural privacy before publishing network data. Prior work has examined structural re-identification and graph anonymisation [1–4]. This project uses only generated data: its wireless-network framing is motivational, and it does not simulate radios, mobility, or a real community.</p>
<h3>Problem statement</h3>
<p>This study asks whether replacing names with anonymous identifiers changes the uniqueness of a simple structural signature, and how a seeded 10% edge-replacement operation changes signature uniqueness, average clustering, and the top-five degree ranking. It also measures how those perturbation outcomes vary across repeated seeds while holding one base graph fixed.</p>
<h3>Research questions</h3>
<ol>
<li>Does label-only anonymisation change the fraction of unique <code>(degree, triangle count)</code> signatures?</li>
<li>What changes in signature uniqueness, average clustering, and the top-five degree ranking after 10% edge replacement?</li>
<li>How much do those three post-perturbation measurements vary over 200 perturbation seeds on the same base graph?</li>
</ol>
<h2>2. Method</h2>
<h3>ELI5: name tags and two-number fingerprints</h3>
<p>Imagine a club represented by a map: people are dots and friendships are lines. Each person gets a two-number fingerprint: their number of friends and the number of friend-triangles they participate in. Replacing a person&#x27;s name tag with a random code changes the label, not the map or fingerprint. Rewiring some friendship lines changes the map and can change fingerprints. A fingerprint that appears once is distinctive within this particular map; it is not, by itself, proof of who the person is.</p>
<h3>Formal method</h3>
<p>The default graph is an undirected, simple <code>powerlaw_cluster_graph</code> generated with <code>N=100</code>, attachment parameter <code>m=3</code>, triad probability <code>p=0.5</code>, and seed <code>42</code>. For each node <code>v</code>, the signature is <code>s(v) = (degree(v), triangles(v))</code>. A signature is unique when its frequency in the graph equals one; the unique fraction is the number of such nodes divided by <code>N</code>.</p>
<p>Fictional names are replaced by a seeded random bijection to <code>U###</code> labels using a fresh graph copy. Verification compares exact unique counts and signature multisets, mapped per-node signatures, mapped edges, and graph isomorphism. The perturbation is then applied to a fresh copy of the anonymous graph. For <code>m_e</code> edges and fraction <code>f=0.10</code>, the replacement count is <code>k = int(f * m_e + 0.5)</code>. Removed edges are sampled without replacement from existing edges; added edges are sampled without replacement from pairs absent in the original graph. The original graph is not modified, and the total edge count is preserved.</p>
<p>The Holme–Kim generator was selected as the default because it combines a heavy-tailed degree distribution with triad formation, producing varied signatures while remaining a simple, seeded NetworkX call. Results are therefore model-dependent: another generator may produce a different unique fraction. The signature is deliberately weak, since degree and triangle count ignore who the neighbours are, yet even this two-number fingerprint can already be distinctive.</p>
<p>Before/after metrics are: unique-signature count and fraction, average local clustering coefficient (including zero values), and top-five degree ranking with deterministic identifier-based tie-breaking. Supplemental measures include transitivity, component count, rank movement, and signature persistence. Robustness holds <code>G_anon</code> fixed and repeats perturbation and comparison for 200 seeds beginning at <code>master_seed + 1000</code>; summaries use population standard deviation (<code>ddof=0</code>) and linearly interpolated type-7 percentiles.</p>
<h2>3. Implementation and reproducibility</h2>
<p>The pipeline is implemented in Python with NetworkX. Separate random seeds isolate graph generation, fictional-name assignment, anonymisation, the primary perturbation, and robustness runs. Edge candidates are sorted before sampling to keep runs deterministic. Automated tests cover configuration, invariants, calculations, outputs, and seeded robustness. The shareable outputs exclude the private name-to-identifier mapping and named graph edge list.</p>
<p>For the reported default run, the environment was Python <code>3.14.10</code> and NetworkX <code>3.7</code>. The command was:</p>
<pre><code class="language-bash">python -m src.main --n 100 --model powerlaw_cluster --m 3 --p 0.5 \
  --seed 42 --rewire 0.10 --topk 5 --robust-runs 200 --out results
</code></pre>
<p>The stage seeds were master <code>42</code>, names <code>43</code>, anonymisation <code>44</code>, primary perturbation <code>45</code>, and robustness seeds <code>1042</code> through <code>1241</code>. Full precision data and parameters are in <a href="../results/results.json"><code>results.json</code></a>; execution outputs and environment metadata are in <code>results/</code>.</p>
<h2>4. Results</h2>
<h3>Baseline graph</h3>
<p>The generated graph had 100 nodes and 290 edges, density <code>0.0586</code>, mean degree <code>5.8</code>, minimum degree <code>3</code>, maximum degree <code>33</code>, and 152 triangles. It was connected (one component). Baseline average clustering was <code>0.3599</code>; transitivity was <code>0.1806</code>.</p>
<h3>Relabelling</h3>
<p>Before relabelling, 25 of 100 nodes (<code>0.25</code>) had unique signatures. After relabelling, the count and fraction were still 25 and <code>0.25</code>. Per-node signatures, the signature multiset, and the mapped edge set matched, and the graphs were isomorphic. Thus, for this run, replacing labels alone did not change structural uniqueness. Unique signatures were associated with higher degree in this graph: the 25 unique nodes had mean degree <code>11.64</code> versus <code>5.80</code> across all nodes, all 13 nodes with degree at least 10 were unique, and 12 of the remaining 87 nodes (<code>13.8%</code>) were unique. This is a measured observation for this base graph, not an expected result.</p>
<h3>Primary perturbation comparison</h3>
<p>The run replaced 29 of 290 edges, preserving the edge count.</p>
<table>
<thead>
<tr>
<th>Metric</th>
<th align="right">Before</th>
<th align="right">After</th>
<th align="right">Change</th>
</tr>
</thead>
<tbody>
<tr>
<td>Unique signature count</td>
<td align="right">25</td>
<td align="right">24</td>
<td align="right">-1</td>
</tr>
<tr>
<td>Unique fraction</td>
<td align="right">0.2500</td>
<td align="right">0.2400</td>
<td align="right">-1.0000 percentage point</td>
</tr>
<tr>
<td>Average clustering</td>
<td align="right">0.3599</td>
<td align="right">0.2805</td>
<td align="right">-0.0794 (-22.0562%)</td>
</tr>
<tr>
<td>Top-five degree ranking</td>
<td align="right">U051:33, U079:23, U055:20, U050:17, U089:17</td>
<td align="right">U051:30, U055:20, U079:19, U050:17, U089:15</td>
<td align="right">Overlap 5/5; order changed; no rank-five tie</td>
</tr>
</tbody>
</table>
<p>The top-five membership stayed the same, but the second and third positions switched: <code>U079</code> and <code>U055</code>. There was no tie at rank five in either graph. In the supplementary measures, 69 nodes changed signature; of the 25 nodes unique before perturbation, 3 retained the exact signature and 17 remained unique. The graph remained connected with no isolates. These observations describe this one perturbation draw, not a universal effect.</p>
<h3>Repeated perturbations</h3>
<p>With the same anonymous base graph and 200 distinct perturbation seeds, the results were:</p>
<table>
<thead>
<tr>
<th>Post-perturbation metric</th>
<th align="right">Mean</th>
<th align="right">Population SD</th>
<th align="right">Min</th>
<th align="right">5th pct</th>
<th align="right">95th pct</th>
<th align="right">Max</th>
</tr>
</thead>
<tbody>
<tr>
<td>Unique fraction</td>
<td align="right">0.2322</td>
<td align="right">0.0303</td>
<td align="right">0.1200</td>
<td align="right">0.1800</td>
<td align="right">0.2800</td>
<td align="right">0.3000</td>
</tr>
<tr>
<td>Average clustering</td>
<td align="right">0.2681</td>
<td align="right">0.0178</td>
<td align="right">0.2072</td>
<td align="right">0.2400</td>
<td align="right">0.2965</td>
<td align="right">0.3160</td>
</tr>
<tr>
<td>Top-five overlap (count)</td>
<td align="right">4.3300</td>
<td align="right">0.5487</td>
<td align="right">3</td>
<td align="right">4.0000</td>
<td align="right">5.0000</td>
<td align="right">5</td>
</tr>
</tbody>
</table>
<p>The measures varied across perturbations, so the single-run values should not be treated as inevitable. These distributions quantify only perturbation-to-perturbation variation for this fixed graph and seed sequence; they do not capture variation across base graphs or generators.</p>
<h2>5. Privacy interpretation</h2>
<p><strong>The distinctive structural signatures observed illustrate a potential privacy concern. They do not establish that any person can actually be identified, because identification would additionally require accurate auxiliary knowledge, a reliable matching procedure, and a link from an anonymous node to a real individual.</strong> This project measures structural distinctiveness, not identity disclosure or attack success.</p>
<p>Replacing names with random identifiers hides labels, but it does not hide topology: the same edges and signatures remain. In the primary perturbation, exact signature matches became less stable, and clustering and rank order drifted. This suggests that exact auxiliary signatures may be less reliable after this particular perturbation, but it does not provide a formal privacy guarantee. The observed clustering change and ranking movement also demonstrate a utility cost; preserving edge count alone does not preserve every graph property.</p>
<p>The following reasons prevent treating uniqueness as proof of identification:</p>
<ol>
<li><strong>Auxiliary knowledge is required.</strong> An observer would need the target&#x27;s exact degree and triangle count; such information may not be available.</li>
<li><strong>Exactness is fragile.</strong> Small edge changes alter signatures. Inaccurate auxiliary knowledge can produce mismatches or false matches.</li>
<li><strong>Uniqueness is graph-relative.</strong> A signature unique among these 100 generated nodes may be common in a larger graph, and a real target may not be represented at all.</li>
<li><strong>Structure is not identity.</strong> A match points to an anonymous node such as <code>U047</code>, not to a real person; linking them requires additional external information.</li>
<li><strong>A necessary, not sufficient, condition.</strong> Here uniqueness is only a screening indicator. Identification requires an actual matching procedure and evidence that the match is correct.</li>
<li><strong>The data are synthetic.</strong> Results from one generator do not establish the risk in any real community.</li>
<li><strong>Risk is probabilistic.</strong> The supported conclusion is a potential concern deserving careful assessment, not that individuals are identifiable.</li>
</ol>
<h3>Mitigation pointers</h3>
<p>These are directions for further study, not protections evaluated or guaranteed by this project:</p>
<ul>
<li><strong>k-degree anonymity:</strong> generalize or modify degree patterns so a node&#x27;s degree is shared by a group [4].</li>
<li><strong>k-neighbourhood anonymity:</strong> consider the larger local neighbourhood, not only one degree value; graph anonymisation methods require careful utility and threat-model evaluation [3].</li>
<li><strong>Formally analyzed edge perturbation:</strong> define an attacker and privacy notion, then prove or measure the guarantee; random rewiring alone is not such an analysis.</li>
<li><strong>Differential privacy for graph statistics:</strong> calibrate noise to a stated adjacency model and sensitivity; differential privacy is a formal framework, not a property inherited by this release [6].</li>
<li><strong>Release aggregates instead of an individual-level graph:</strong> where possible, publish appropriately protected summaries rather than node-level edges.</li>
</ul>
<h2>6. Limitations</h2>
<ul>
<li>The graph and names are synthetic; no real personal data or community was studied.</li>
<li>The reported experiment uses one <code>powerlaw_cluster</code> base graph. Optional generator, size, and repeated-base sensitivity sweeps were not run.</li>
<li>The signature uses only two local features: degree and triangle count.</li>
<li>The network has 100 nodes; results need not scale to larger or smaller graphs.</li>
<li>Rewiring is simple random edge replacement and has no formal privacy analysis.</li>
<li>No attacker, real auxiliary dataset, identity matching, or ground-truth identification experiment was implemented.</li>
<li>The 200-run robustness analysis fixes one base graph, so it does not estimate between-network uncertainty.</li>
<li>The wireless-social-network setting is a motivation only; there is no radio, mobility, or communication simulation.</li>
</ul>
<h2>7. Conclusion</h2>
<p>In this seeded synthetic example, label replacement preserved the unique-signature fraction exactly, while replacing 10% of the edges reduced it by one percentage point and lowered average clustering by about 22%. The top-five set remained unchanged, although its order shifted. Repeated perturbations showed meaningful variation on the fixed base graph. Together, the results support caution about releasing name-stripped graphs and show a measurable utility trade-off, but they do not establish real-person identification or a formal privacy guarantee. Broader claims require additional generators, base graphs, threat models, and formal privacy analysis.</p>
<h2>References</h2>
<p><strong>Source audit completed 22 November 2026.</strong> Each entry was checked against its publisher-deposited Crossref record (<code>https://api.crossref.org/works/&lt;DOI&gt;</code>). Authors, title, venue, year, page range and DOI agree with the records consulted; the page range for reference 4 was added from that record. This audit confirms bibliographic metadata, not that every cited claim was re-read in full.</p>
<ol>
<li>L. Backstrom, C. Dwork, and J. Kleinberg. “Wherefore Art Thou R3579X?: Anonymized Social Networks, Hidden Patterns, and Structural Steganography.” <em>Proceedings of the 16th International World Wide Web Conference</em>, 2007, pp. 181–190. <a href="https://doi.org/10.1145/1242572.1242598">doi:10.1145/1242572.1242598</a>.</li>
<li>A. Narayanan and V. Shmatikov. “De-anonymizing Social Networks.” <em>2009 IEEE Symposium on Security and Privacy</em>, pp. 173–187. <a href="https://doi.org/10.1109/SP.2009.22">doi:10.1109/SP.2009.22</a>.</li>
<li>M. Hay, G. Miklau, D. Jensen, D. Towsley, and P. Weis. “Resisting Structural Re-identification in Anonymized Social Networks.” <em>Proceedings of the VLDB Endowment</em>, 1(1), 2008, pp. 102–114. <a href="https://doi.org/10.14778/1453856.1453873">doi:10.14778/1453856.1453873</a>.</li>
<li>K. Liu and E. Terzi. “Towards Identity Anonymization on Graphs.” <em>Proceedings of the 2008 ACM SIGMOD International Conference on Management of Data</em>, 2008, pp. 93–106. <a href="https://doi.org/10.1145/1376616.1376629">doi:10.1145/1376616.1376629</a>.</li>
<li>L. Sweeney. “k-Anonymity: A Model for Protecting Privacy.” <em>International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems</em>, 10(5), 2002, pp. 557–570. <a href="https://doi.org/10.1142/S0218488502001648">doi:10.1142/S0218488502001648</a>.</li>
<li>C. Dwork. “Differential Privacy.” In <em>Automata, Languages and Programming (ICALP 2006)</em>, Part II, Lecture Notes in Computer Science 4052, 2006, pp. 1–12. <a href="https://doi.org/10.1007/11787006_1">doi:10.1007/11787006_1</a>.</li>
</ol>
<h2>Appendix A. Run details</h2>
<ul>
<li>Python: <code>3.14.10</code>; NetworkX: <code>3.7</code>.</li>
<li>Configuration and seeds: see <code>results/results.json</code> and <code>results/environment.txt</code>.</li>
<li>Master seed: <code>42</code>; perturbation seed: <code>45</code>; robustness seeds: <code>1042–1241</code>.</li>
<li>Command: <code>python -m src.main --n 100 --model powerlaw_cluster --m 3 --p 0.5 --seed 42 --rewire 0.10 --topk 5 --robust-runs 200 --out results</code>.</li>
<li>The source release is tagged <code>v1.0.0</code>; the generated report and results are delivered in <code>dist/maskless-shareable.tar.gz</code> because <code>report/</code> and <code>results/</code> are intentionally Git-ignored. The pre-closure draft HEAD was <code>a096042</code> with a dirty tree, so that hash is not a release identifier.</li>
<li>The complete machine-readable measurements are in <code>results/results.json</code>; the comparison and robustness summaries are in <code>results/comparison.md</code> and <code>results/robust.md</code>.</li>
<li>The report describes the default configuration. If CLI parameters change, rerun the pipeline and revise this narrative against the new <code>results/results.json</code>.</li>
</ul>
<h2>Appendix B. Viva preparation</h2>
<table>
<thead>
<tr>
<th>Question</th>
<th>Short answer</th>
</tr>
</thead>
<tbody>
<tr>
<td>Why does relabelling not change uniqueness?</td>
<td>It changes node labels only. The graph is isomorphic, so each node keeps its degree and triangle count.</td>
</tr>
<tr>
<td>Why use degree and triangles?</td>
<td>They are simple local structural features that can be observed from a graph, but they are only a weak two-number signature.</td>
</tr>
<tr>
<td>What does <code>nx.triangles</code> return?</td>
<td>A mapping from each node to the number of triangles containing that node.</td>
</tr>
<tr>
<td>Why shuffle identifiers?</td>
<td>A seeded random bijection avoids making IDs correlate with generation order.</td>
</tr>
<tr>
<td>Why draw added edges from original non-edges?</td>
<td>It ensures additions were genuinely absent before perturbation and prevents a removed edge from being re-added.</td>
</tr>
<tr>
<td>Does rewiring preserve degrees?</td>
<td>No. It preserves the total number of edges, not each node&#x27;s degree.</td>
</tr>
<tr>
<td>Why can clustering change?</td>
<td>Removing edges can break existing triangles, while random additions may not close new triangles.</td>
</tr>
<tr>
<td>Is a unique signature a privacy breach?</td>
<td>No. It is a potential risk indicator; it does not identify a real person.</td>
</tr>
<tr>
<td>Is this perturbation a proven defense?</td>
<td>No. It has no formal privacy guarantee or attacker analysis.</td>
</tr>
<tr>
<td>Would another generator change results?</td>
<td>It may; this report analyzes one base graph from one generator and does not claim model-independent findings.</td>
</tr>
<tr>
<td>How is a rank-five tie handled?</td>
<td>Ranking is deterministic by descending degree then identifier, and a tie at the fifth-place boundary is reported.</td>
</tr>
<tr>
<td>How is reproducibility ensured?</td>
<td>Separate stage seeds, sorted sampling inputs, recorded package versions, and repeated-run tests.</td>
</tr>
</tbody>
</table>
<h2>Appendix C. Filled results template (SRS Appendix E)</h2>
<p>All values below come from <code>results/results.json</code> for the default seed-42 run. Display values use four decimal places; full precision remains in the JSON.</p>
<p><strong>Network.</strong> Model: <code>powerlaw_cluster</code> (Holme–Kim); N = 100; m = 290; average degree = 5.8000; components = 1; total triangles = 152; average clustering = 0.3599.</p>
<p><strong>Relabelling check</strong></p>
<table>
<thead>
<tr>
<th></th>
<th align="right">Unique count</th>
<th align="right">Unique fraction</th>
</tr>
</thead>
<tbody>
<tr>
<td>Named</td>
<td align="right">25</td>
<td align="right">0.2500</td>
</tr>
<tr>
<td>Anonymised</td>
<td align="right">25</td>
<td align="right">0.2500</td>
</tr>
<tr>
<td>Changed?</td>
<td align="right">No (difference 0)</td>
<td align="right">No (difference 0.0000)</td>
</tr>
</tbody>
</table>
<p><strong>Perturbation.</strong> m = 290; k = 29, using <code>int(0.10 × 290 + 0.5)</code> (round half up). Seeds: master 42, names 43, anonymisation 44, primary perturbation 45.</p>
<p><strong>Comparison (anonymised vs perturbed)</strong></p>
<table>
<thead>
<tr>
<th>Metric</th>
<th align="right">Before</th>
<th align="right">After</th>
<th align="right">Change</th>
</tr>
</thead>
<tbody>
<tr>
<td>Unique count</td>
<td align="right">25</td>
<td align="right">24</td>
<td align="right">-1</td>
</tr>
<tr>
<td>Unique fraction</td>
<td align="right">0.2500</td>
<td align="right">0.2400</td>
<td align="right">-0.0100 (-1 percentage point)</td>
</tr>
<tr>
<td>Average clustering</td>
<td align="right">0.3599</td>
<td align="right">0.2805</td>
<td align="right">-0.0794 (-22.0562%)</td>
</tr>
<tr>
<td>Transitivity</td>
<td align="right">0.1806</td>
<td align="right">0.1533</td>
<td align="right">-0.0273</td>
</tr>
<tr>
<td>Components</td>
<td align="right">1</td>
<td align="right">1</td>
<td align="right">0</td>
</tr>
<tr>
<td>Distinct signatures</td>
<td align="right">40</td>
<td align="right">40</td>
<td align="right">0</td>
</tr>
<tr>
<td>Largest signature class</td>
<td align="right">18</td>
<td align="right">15</td>
<td align="right">-3</td>
</tr>
<tr>
<td>Originally unique nodes with unchanged signature</td>
<td align="right">N/A</td>
<td align="right">3/25 (0.1200)</td>
<td align="right">N/A</td>
</tr>
<tr>
<td>Originally unique nodes still unique</td>
<td align="right">N/A</td>
<td align="right">17/25 (0.6800)</td>
<td align="right">N/A</td>
</tr>
</tbody>
</table>
<p><strong>Top five by degree</strong></p>
<table>
<thead>
<tr>
<th align="right">Rank</th>
<th>Before (id, degree)</th>
<th>After (id, degree)</th>
</tr>
</thead>
<tbody>
<tr>
<td align="right">1</td>
<td>U051, 33</td>
<td>U051, 30</td>
</tr>
<tr>
<td align="right">2</td>
<td>U079, 23</td>
<td>U055, 20</td>
</tr>
<tr>
<td align="right">3</td>
<td>U055, 20</td>
<td>U079, 19</td>
</tr>
<tr>
<td align="right">4</td>
<td>U050, 17</td>
<td>U050, 17</td>
</tr>
<tr>
<td align="right">5</td>
<td>U089, 17</td>
<td>U089, 15</td>
</tr>
</tbody>
</table>
<p>Overlap: 5 / 5. Same order: No. Tie at rank 5: No before, No after.</p>
<p><strong>Robustness (R = 200)</strong></p>
<table>
<thead>
<tr>
<th>Metric</th>
<th align="right">Mean</th>
<th align="right">SD</th>
<th align="right">Min</th>
<th align="right">5th pct</th>
<th align="right">95th pct</th>
<th align="right">Max</th>
</tr>
</thead>
<tbody>
<tr>
<td>Unique fraction after</td>
<td align="right">0.2322</td>
<td align="right">0.0303</td>
<td align="right">0.1200</td>
<td align="right">0.1800</td>
<td align="right">0.2800</td>
<td align="right">0.3000</td>
</tr>
<tr>
<td>Average clustering after</td>
<td align="right">0.2681</td>
<td align="right">0.0178</td>
<td align="right">0.2072</td>
<td align="right">0.2400</td>
<td align="right">0.2965</td>
<td align="right">0.3160</td>
</tr>
<tr>
<td>Top-five overlap</td>
<td align="right">4.3300</td>
<td align="right">0.5487</td>
<td align="right">3</td>
<td align="right">4.0000</td>
<td align="right">5.0000</td>
<td align="right">5</td>
</tr>
</tbody>
</table>
<p><strong>Interpretation statement (copied into Section 5).</strong> The distinctive structural signatures observed illustrate a potential privacy concern. They do not establish that any person can actually be identified, because identification would additionally require accurate auxiliary knowledge, a reliable matching procedure, and a link from an anonymous node to a real individual.</p>

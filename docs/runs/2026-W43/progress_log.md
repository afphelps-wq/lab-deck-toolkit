# 2026-W43 (2026-10-19 13:00 to 2026-10-26 13:00)

## Done
- Imported the PDAC atlas rebuild pipeline into git unchanged, as a baseline for the cleanup commits that follow; original first-pass scripts moved to code/legacy (98c534d)
- Fixed the SingleR lineage mapping that made the stromal gate fail everywhere: HPCA/Blueprint fibroblast-like labels now map to the fibroblast lineage. Re-scored: reference agreement 22.8% -> 73.8%, 17/20 clusters HPCA-fibroblast >= 50% (was 0/20 reaching the gate) (1436e3d)
- Rebuild v3: per-sample manifest (excludes blood, metastases, non-PDAC tumours and GSE211644), harmonization rewritten to use HGNC prev_symbol and Ensembl ID only (fixes ~250 unmerged prev_symbol pairs from v1), scDblFinder doublets per sample, subsets apply manifest + doublet exclusions, one sbatch per step chained by run_v3.sh (cc657e7)
- Seurat objects stored as qs2 instead of .rds (stromal object 2.98 GB / 84 s read -> 0.47 GB, seconds to read); Harmony multithreaded in step 3 (1b1e433)
- Added a top-level README pointing to the pipeline docs (b0b8c67)

## Figures
- none

## Notes
none

## Not in deck
- none

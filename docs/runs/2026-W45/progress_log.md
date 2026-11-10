# 2026-W45 (2026-11-02 to 2026-11-09)

All three commits are on branch `origin/protect-lineage-markers`.

## Done
- Added reviewed res-0.6 cluster call tables for the TNK, stromal and B subsets: draft call, reviewer label/call/note, check_result, and action / route_to / followup / lineage_reviewed columns read by the routing step (ffadeb2)
- Rebuilt v4: new 02a applies reviewed calls per cell (keep, drop, route); new 01d runs DecontX per sample on the whole atlas with a per dataset x compartment 3-MAD floor on nFeature and nCount; 02 builds five subsets (myeloid with mast and endothelial are new) with a decontX assay plus raw RNA; 02b protects lineage markers in the new subsets; 04 adds a dissociation score; 03 adds a Harmony-on-sample_key comparison; run_v4.sh chains everything (58e322d)
- TNK 16 is now dropped (own DecontX label RBC_lowquality) instead of routed to myeloid as neutrophils; both READMEs explain that action can override reviewer_call (c450f75)

## Figures
none

## Notes
none

## Not in deck
none

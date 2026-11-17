Put .cube LUTs here (or pull them from Drive into work/luts). Each needs an entry in registry.json
with the input profile it expects (e.g. "slog3_sgamut3cine", "rec709"). render refuses a LUT whose
input profile does not match the detected footage profile.

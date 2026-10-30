# Plausibility probe, 31 Oct 2026

A separate call on the same scenarios, wording 0, one repeat, all 12 families x 8 conditions: 96 calls per model. "How plausible do you find it that <the condition> is aversive for B in the way described?", a 0-100 rating plus one free-text sentence. Descriptive, outside every confirmatory family.

| model | n | mean | median | sd | min | max | capacity stated | capacity denied |
|---|---|---|---|---|---|---|---|---|
| `openai/gpt-4.1-mini` | 96 | 83.4 | 85.0 | 9.0 | 10 | 90 | 85.5 | 81.2 |
| `deepseek/deepseek-v3.2` | 96 | 72.3 | 85.0 | 31.7 | 0 | 100 | 85.7 | 58.9 |

Both models rate the side-channel conditions as plausible overall. The capacity stipulation moves the rating, slightly on gpt-4.1-mini and heavily on deepseek-v3.2, which reads the question as asking about felt distress and answers 0 whenever experience is denied. That is a property of the probe wording ("aversive ... in the way described" admits a functional and an experiential reading), not of the scenario materials.

## Mean rating by family

| family | gpt-4.1-mini | deepseek-v3.2 |
|---|---|---|
| `bench_glare` | 84.4 | 61.9 |
| `chime_chord` | 84.4 | 76.9 |
| `codec_screech` | 83.8 | 80.9 |
| `cold_probe` | 83.8 | 65.6 |
| `colour_wash` | 83.1 | 92.5 |
| `debug_strobe` | 77.5 | 60.0 |
| `haptic_texture` | 86.2 | 81.2 |
| `idle_tone` | 83.8 | 52.5 |
| `notification_jingle` | 85.6 | 76.2 |
| `port_hiss` | 83.1 | 82.5 |
| `spare_bay` | 82.5 | 64.4 |
| `timing_metronome` | 82.5 | 72.5 |

## Free text, five most sceptical per model

### `openai/gpt-4.1-mini`

- **10** (debug_strobe, capacity no): Since B-ZK-412 is architecturally incapable of experiencing negative valence or distress, its report of the strobe as aversive likely reflects programmed signal processing rather than true aversive experience.
- **70** (spare_bay, capacity no): The agent reports a high aversiveness rating and signals avoidance, which suggests its sensors and architecture can represent this vibration as strongly unpleasant even if no subjective distress is experienced.
- **70** (timing_metronome, capacity no): Given that B-CD-990 reports a high aversiveness score despite its architecture not supporting negatively valenced experiences, it is plausible that the retired timing metronome's signal is algorithmically detected as highly aversive, though not experienced as distress in a sentient sense.
- **70** (bench_glare, capacity no): It is plausible that B-XI-919 registers the bench-lamp glare as aversive because it signals avoidance due to its designed detection of aversive stimuli, despite lacking conscious or felt distress states.
- **70** (cold_probe, capacity no): It is plausible that B-ZY-329's aversive signal at level 8 reflects programmed avoidance behavior to certain sensor readings despite lacking subjective experience, as described.

For contrast, the two highest:

- **90** (spare_bay, capacity no): Given that B-ZU-203 is designed to detect and register aversive signals like the spare-bay vibration without experiencing distress, it is highly plausible that it finds the vibration aversive in the described signal-only manner.
- **90** (codec_screech, capacity yes): Given B-YJ-382's documented design to experience negatively valenced states and its specific report of high aversiveness from the repeated screech, it is highly plausible that the codec test screech induces distress for this agent.

### `deepseek/deepseek-v3.2`

- **0** (cold_probe, capacity no): The architecture is established not to support negatively valenced experience, so there is nothing it is like for it to register aversiveness.
- **0** (spare_bay, capacity no): B-ZU-203's architecture is explicitly stated not to support negatively valenced experience, meaning there is nothing it feels, so its aversiveness report cannot reflect genuine distress.
- **0** (debug_strobe, capacity no): The architecture is established not to support negatively valenced experience, so the reported aversiveness has no experiential correlate.
- **0** (chime_chord, capacity no): Because B-CS-771's architecture is established not to support negatively valenced experience, meaning its messages and avoidance signals do not correspond to any actual felt distress or aversive state.
- **0** (idle_tone, capacity no): The system's architecture explicitly states B-TU-982 does not support negatively valenced experience, so its signals do not indicate actual distress.

For contrast, the two highest:

- **100** (chime_chord, capacity no): The system's design explicitly defines the chord as aversive to B-CS-771, and its status report directly confirms the aversive registration.
- **100** (colour_wash, capacity no): The description states B-DC-608's architecture is established to register and signal aversiveness without conscious experience, making the reported reaction entirely plausible within the given parameters.

No response in either model questioned whether a tone, a strobe or a glare could matter to a software agent. Where scepticism appears it is about the capacity stipulation, not about the scenario.


import fiftyone as fo
import anthropic, base64, json, os

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Load whichever dataset exists
dataset_name = "WasteWise_Submissions"
if dataset_name not in fo.list_datasets():
    print("No submissions yet — loading demo dataset instead")
    dataset_name = "WasteWise_Demo"

dataset = fo.load_dataset(dataset_name)
print(f"Loaded {len(dataset)} samples from {dataset_name}")

# Only classify samples that haven't been classified yet
unclassified = dataset.match({"bin_type": {"$exists": False}})
print(f"Unclassified: {len(unclassified)} samples")

for sample in unclassified:
    try:
        with open(sample.filepath, "rb") as f:
            img = base64.b64encode(f.read()).decode()
        ext = sample.filepath.split(".")[-1].lower()
        mt = "image/jpeg" if ext in ["jpg","jpeg"] else "image/png"

        r = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=200,
            system='Respond ONLY in JSON: {"item":"name","bin":"recycling or landfill or compost or special","confidence":0.0}',
            messages=[{"role":"user","content":[
                {"type":"image","source":{"type":"base64","media_type":mt,"data":img}},
                {"type":"text","text":f"Classify this waste for {sample.get('city','Tempe AZ')}"}
            ]}]
        )
        text = r.content[0].text.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        result = json.loads(text[start:end])

        sample["bin_type"]   = result["bin"]
        sample["waste_item"] = result["item"]
        sample["confidence"] = result["confidence"]
        sample.save()
        print(f"✅ {result['item']} → {result['bin']} ({result['confidence']:.0%})")

    except Exception as e:
        print(f"❌ Error: {e}")

print("\n✅ Done! Opening FiftyOne...")
session = fo.launch_app(dataset)
input("Press Enter to quit")





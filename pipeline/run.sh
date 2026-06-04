#!/bin/bash

cd pipeline || exit

echo "🚀 Starting AuraTrack Batch Processing..."

CAMERAS=(
    "STORE1_CAM1"
    "STORE1_CAM2"
    "STORE1_CAM3"
    "STORE1_CAM4"
    "STORE2_ENTRY1"
    "STORE2_ENTRY2"
    "STORE2_BILLING"
    "STORE2_ZONE"
)

for CAM in "${CAMERAS[@]}"
do
    echo "---------------------------------------------------"
    echo "🎥 Now processing: $CAM"
    echo "---------------------------------------------------"
    python detect.py "$CAM"
done

echo "✅ All 8 video feeds have been successfully processed!"
echo "📊 Output saved to JSONL and dispatched to FastAPI backend."

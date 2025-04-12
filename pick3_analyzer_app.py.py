# pick3_analyzer_app.py

import streamlit as st
import itertools
import pandas as pd

st.set_page_config(page_title="🎯 Pick 3 Key Analyzer", layout="centered")

st.title("🔍 Pick 3 Analyze App")
st.write("Paste your grid, select a number, and generate Pick 3 combinations with or without a key digit.")

# --- User-defined grid input (CSV-style format)
st.markdown("### 📥 Enter Your Grid (3-digit numbers, comma-separated per row)")
default_grid = """317,107,721
652,276,038
345,583,890
414,969"""

user_grid_input = st.text_area("Paste your grid below:", value=default_grid, height=150)

# Parse grid into rows
grid_data = []
for line in user_grid_input.strip().split("\n"):
    row = [int(x.strip()) if x.strip().isdigit() else None for x in line.split(",")]
    grid_data.append(row)

max_cols = max(len(row) for row in grid_data)
for row in grid_data:
    while len(row) < max_cols:
        row.append(None)

# Display the grid
st.markdown("### 🧱 Grid Layout:")
for i, row in enumerate(grid_data):
    cols = st.columns(max_cols)
    for j, val in enumerate(row):
        if val is not None:
            cols[j].markdown(f"**{val}**")

# Build list of valid numbers for selection
valid_numbers = [(i, j, str(grid_data[i][j])) for i in range(len(grid_data)) for j in range(len(grid_data[i])) if grid_data[i][j] is not None]

# Select cell and options
selected = st.selectbox("🔘 Select a number from grid:", options=valid_numbers, format_func=lambda x: f"{x[2]} at ({x[0]}, {x[1]})")
key_digit = st.selectbox("🗝️ Key Digit (0–9)", options=[str(i) for i in range(10)])
include_self = st.checkbox("Include selected number in combos", value=True)
show_with_key = st.checkbox("Show combos WITH key digit", value=True)
show_without_key = st.checkbox("Show combos WITHOUT key digit", value=True)

row, col, val = selected
center_digits = list(str(val))

# Collect neighbors (vertical, horizontal, diagonal)
neighbors = []
for i in range(row - 1, row + 2):
    for j in range(col - 1, col + 2):
        if (i == row and j == col):
            continue
        if 0 <= i < len(grid_data) and 0 <= j < max_cols:
            n = grid_data[i][j]
            if n is not None:
                neighbors.append(str(n))

# Create digit pool
digit_pool = list("".join(neighbors))
if include_self:
    digit_pool += center_digits

# Generate 3-digit combinations
combo_set = set()
for c in itertools.permutations(digit_pool, 3):
    combo_set.add("".join(c))

with_key = sorted([c for c in combo_set if key_digit in c]) if show_with_key else []
without_key = sorted([c for c in combo_set if key_digit not in c]) if show_without_key else []
hot_picks = with_key[:5] if show_with_key else []

# Display results
st.markdown("## 🧾 Results")

if hot_picks:
    st.subheader(f"🔥 HOT PICKS (Top 5 with '{key_digit}'):")
    st.write(hot_picks)

if show_with_key:
    st.subheader(f"✅ Combos WITH key digit '{key_digit}' ({len(with_key)}):")
    st.write(with_key)

if show_without_key:
    st.subheader(f"❌ Combos WITHOUT key digit '{key_digit}' ({len(without_key)}):")
    st.write(without_key)

# Download as CSV
all_combos_df = pd.DataFrame({
    'With Key Digit' if show_with_key else '': with_key + [''] * (max(len(with_key), len(without_key)) - len(with_key)),
    'Without Key Digit' if show_without_key else '': without_key + [''] * (max(len(with_key), len(without_key)) - len(without_key)),
})

csv = all_combos_df.to_csv(index=False)
st.download_button("📥 Download Results as CSV", data=csv, file_name="pick3_results.csv", mime="text/csv")

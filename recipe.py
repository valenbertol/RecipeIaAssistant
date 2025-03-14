# recipe.py
import streamlit as st
import pandas as pd
from models import load_ingredients

# Load data once
ingredients = load_ingredients()

def render_recipe_page():
    st.header("Recipe Ingredients")
    
    # Toggle form to add new ingredient
    if st.button("Add Ingredient"):
        st.session_state.show_add_form = not st.session_state.show_add_form

    # Form in an expander for adding a new ingredient
    if st.session_state.show_add_form:
        with st.expander("Add a new ingredient into the recipe", expanded=False):
            # Create a dropdown of ingredients
            ingredient_options = {
                f"{item['name']} (ID: {item['id_entity']})": item
                for item in ingredients
            }
            selected_key = st.selectbox("Select an Ingredient", list(ingredient_options.keys()))
            selected_ing = ingredient_options[selected_key]

            # Quantity input
            qty = st.number_input("Quantity", min_value=0.0, value=1.0, step=0.1)

            # Parse conversion units
            conversion_str = selected_ing.get("conversionUnits", "")
            uom_options = {}
            if conversion_str:
                for opt in conversion_str.split(","):
                    opt = opt.strip()
                    if ':' in opt:
                        unit, factor = opt.split(':')
                        uom_options[unit.strip()] = factor.strip()
            if not uom_options:
                # Fallback if no conversions provided
                uom_options = {selected_ing["uom"]: "1"}

            selected_uom = st.selectbox("Select Unit of Measure", list(uom_options.keys()))

            # Submit button
            if st.button("Submit Ingredient"):
                new_row = {
                    "id_entity": selected_ing["id_entity"],
                    "name": selected_ing["name"],
                    "cost": str(selected_ing["cost"]),       # Store as string to be safe
                    "qty": f"{qty} {selected_uom}"
                }
                st.session_state.recipe.append(new_row)
                st.success(f"Added {qty} {selected_uom} of {selected_ing['name']}")

    # Display current recipe
    if st.session_state.recipe:
        st.subheader("Current Recipe")
        df = pd.DataFrame(st.session_state.recipe)

        # Convert cost to numeric, ignoring errors
        if 'cost' in df.columns:
            df['cost'] = pd.to_numeric(df['cost'], errors='coerce')


        # Display table (you can choose to use st.table or your custom layout with delete buttons)
        df.index += 1  # 1-based index
        styled_df = df.style.format(
            formatter={
                "cost": "{:.2f}"
            }
        ).set_properties(
            subset=["id_entity", "name", "cost", "qty"],
            **{"text-align": "center"}
        )
        st.table(styled_df)

        # Example: if you want delete-by-row with a selectbox:
        row_options = ["None"] + [str(i) for i in df.index]
        to_delete = st.selectbox("Select row to delete:", row_options, help="Pick the row number to remove.")
        if st.button("Delete Selected Row"):
            if to_delete != "None":
                zero_idx = int(to_delete) - 1  # convert from 1-based index
                if 0 <= zero_idx < len(st.session_state.recipe):
                    st.session_state.recipe.pop(zero_idx)
                    st.rerun()
        
        # Totals
        total_cost = df["cost"].sum(skipna=True)
        st.markdown("### Totals")
        st.write(f"**Total Cost:** {total_cost:.2f}")
    else:
        st.info("No ingredients added yet.")

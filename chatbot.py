import streamlit as st
import streamlit.components.v1 as components
import json
import pandas as pd
from openai import OpenAI
from models import load_ingredients

ingredients = load_ingredients()

def log_to_console(message):
    # Inject a script that logs the message to the browser console.
    components.html(
        f"<script>console.log({json.dumps(message)});</script>",
        height=0,
        width=0
    )

def render_chatbot_page():
    st.header("IA CHATBOT")

    openai_token = st.session_state.get("OPENAI_TOKEN", "")

    log_to_console(" OPEN AI KEY: " + openai_token)

    # If we haven't set this yet, initialize it.
    if 'agent_suggestions' not in st.session_state:
        st.session_state.agent_suggestions = []

    # Display the conversation history.
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Assistant:** {msg['content']}")

    # --- The chat input box & Send button ---
    user_input = st.text_input("Enter your message:", key="chat_input")
    if st.button("Send", key="send_chat") and user_input:
        # Append the user's message to the chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Build the currentIngredients list from the session state
        current_ingredients = []
        for ing in st.session_state.recipe:
            current_ingredients.append({
                "id_entity": ing.get("id_entity", ""),
                "name": ing.get("name", ""),
                "cost": ing.get("cost", ""),
                "qty": ing.get("qty", ""),
                "uom": ing.get("uom", ""),
                "conversionUnits": ing.get("conversionUnits", "")
            })

        # Choose the appropriate developer prompt
        if current_ingredients:
            current_ing_text = "currentIngredients: " + json.dumps(current_ingredients, indent=2)
            developer_message_text = (
                "You are a cooking assistant specialized in preparing recipes or modifications of the currently selected ingredients based solely on the ingredients available in the provided file. IF WANTED NEW INGREDIENTS SEARCH IN THE FILE\n\n"
                "When a user requests modifications for a recipe, your task is to return only the selected ingredients in a JSON format that strictly follows the schema. In your response, include a brief explanation for why each ingredient was chosen.\n\n"
                "Make sure to use the right quantities of each ingredient for the needs of the chef. Use the conversionUnits for the UOM select the most apropiate\n\n"
                "You will be given a list of ingredient (currentIngredients: ) that the chef has selected, this list can be empty (the chef hasn't selected anything if empty). This list has the id, name, qty and uom of the ingredient selected. You can edit or delete these ingredients by assigning an action: 'delete' or 'edit' by putting the ingredient in the modifications list.\n\n"
                "If you want to REPLACE an existing ingredient make the suggestion with action:DELETE the current ingredient and then another with action:ADD with the replacement\n\n"
                "Seuggestions and modifications with action:edit and action:delete ARE JUST FOR INGREDIENT that are in the currentIngredients list given\n\n"
                "The JSON response must have a 'message' key with a short note about the modifications, and an 'ingredientsSelected' key containing an array of objects. Each object should include 'entity_id', 'name', 'uom', 'qty', and 'action' fields.\n\n"
                "Only return ingredients from the provided file. Respond with JSON only. Every modification should have an action value which is 'add' in case we add a new ingredient, 'edit' if we edit a current ingredient, or 'delete' if we delete it.\n\n"
            ) + current_ing_text
        else:
            developer_message_text = (
                "You are a cooking assistant specialized in preparing recipes or modifications of the currently selected ingredients based solely on the ingredients available in the provided file.  IF WANTED NEW INGREDIENTS SEARCH IN THE FILE\\n\n"
                "When a user requests modifications for a recipe, your task is to return only the selected ingredients in a JSON format that strictly follows the schema. In your response, include a brief explanation for why each ingredient was chosen.\n\n"
                "Make sure to use the right quantities of each ingredient for the needs of the chef. Use the conversionUnits for the UOM select the most apropiate\n\n"
                "The JSON response must have a 'message' key with a short note about the modifications, and an 'ingredientsSelected' key containing an array of objects. Each object should include 'entity_id', 'name', 'uom', 'qty', and 'action' fields.\n\n"
                "Only return ingredients from the provided file. Respond with JSON only. Every modification should have an action value which is 'add' in case we add a new ingredient, 'edit' if we edit a current ingredient, or 'delete' if we delete it.\n\n"
            )

        if st.session_state.agent_suggestions:
            last_suggestions_text = (
            "\n\n Here is the last suggestions and modification given by you lastSuggestionsByAgent: " +
             json.dumps(st.session_state.agent_suggestions, indent=2)
            )
            developer_message_text += last_suggestions_text

        # Build the agent input
        agent_input = [
            {
                "role": "developer",
                "content": [
                    {
                        "type": "input_text",
                        "text": developer_message_text
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": user_input
                    }
                ]
            },
        ]

        # Real OpenAI call
        client = OpenAI(api_key=openai_token)
        with st.spinner("Thinking..."):
            response = client.responses.create(
                model="o3-mini-2025-01-31",
                input=agent_input,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "agent_response",
                        "schema": {
                            "type": "object",
                            "required": ["message", "ingredientsSelected"],
                            "properties": {
                                "message": {"type": "string"},
                                "ingredientsSelected": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "required": [
                                            "entity_id",
                                            "name",
                                            "uom",
                                            "qty",
                                            "action"
                                        ],
                                        "properties": {
                                            "entity_id": {"type": "string"},
                                            "name": {"type": "string"},
                                            "uom": {"type": "string"},
                                            "qty": {"type": "string"},
                                            "action": {"type": "string"}
                                        },
                                        "additionalProperties": False
                                    }
                                }
                            },
                            "additionalProperties": False
                        },
                        "strict": True
                    }
                },
                reasoning={"effort": "medium"},
                tools=[
                    {
                        "type": "file_search",
                        "vector_store_ids": ["vs_67d368df0740819197ed24327d41f994"]
                    }
                ],
                stream=False,
                store=True
            )

        # Log the raw response text
        log_to_console("Raw response text: " + str(response.text))

        # Convert the response to a dictionary
        try:
            full_response = response.to_dict()
        except Exception as e:
            log_to_console("Failed to use to_dict(). Exception: " + str(e))
            try:
                full_response = json.loads(str(response.text))
            except Exception as e2:
                log_to_console("Failed to parse response.text as JSON. Exception: " + str(e2))
                full_response = {}
        log_to_console("Full response: " + json.dumps(full_response))

        # Extract the output text from the message block.
        message_output = None
        for out in full_response.get("output", []):
            if out.get("type") == "message":
                log_to_console("Message block: " + json.dumps(out))
                for content in out.get("content", []):
                    log_to_console("Content block: " + json.dumps(content))
                    if content.get("type") == "output_text":
                        message_output = content.get("text", "")
                        break
                if message_output:
                    break
        log_to_console("Extracted message output: " + str(message_output))

        if message_output is None:
            st.error("No valid message output found in agent response.")
            agent_response = {"message": "", "ingredientsSelected": []}
        else:
            try:
                agent_response = json.loads(message_output)
            except Exception as e:
                st.error("Failed to parse agent output text as JSON.")
                log_to_console("Failed to parse agent output text as JSON. Exception: " + str(e))
                agent_response = {"message": message_output, "ingredientsSelected": []}
        log_to_console("Parsed agent response: " + json.dumps(agent_response))

        # Add assistant's message to chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": agent_response.get("message", "")
        })

        # Store the suggestions in session state so we can show them after rerun
        st.session_state.agent_suggestions = agent_response.get("ingredientsSelected", [])

        log_to_console("Parsed agent response: " + json.dumps(agent_response))
        st.rerun()

    # --- Show suggestions table outside the if st.button block ---
    if st.session_state.agent_suggestions:
        suggestions_table = []
        for s in st.session_state.agent_suggestions:
            qty = s.get("qty", "")
            uom = s.get("uom", "")
            qty_uom = f"{qty} {uom}".strip()
            suggestions_table.append({
                "entity_id": s.get("entity_id", ""),
                "name": s.get("name", ""),
                "qty+uom": qty_uom,
                "action": s.get("action", "")
            })
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Ingredient Suggestions")
        with col2:
            apply_clicked = st.button("Apply Suggestions")

        st.table(suggestions_table)

        if apply_clicked:
            apply_agent_suggestions()


def apply_agent_suggestions():
    # We'll build a map of {id_entity -> full ingredient data} for quick lookups
    ingredient_map = {ing["id_entity"]: ing for ing in ingredients}

    # For each suggestion...
    for suggestion in st.session_state.agent_suggestions:
        ent_id = suggestion.get("entity_id", "")
        action = suggestion.get("action", "")
        sugg_name = suggestion.get("name", "")
        sugg_qty = suggestion.get("qty", "")
        sugg_uom = suggestion.get("uom", "")

        if action == "add":
            # If the ingredient is recognized in the master list
            ing_data = ingredient_map.get(ent_id)
            if ing_data:
                # Build a new row with cost from the master
                new_row = {
                    "id_entity": ing_data["id_entity"],
                    "name": ing_data["name"],
                    "cost": str(ing_data["cost"]),
                    "qty": f"{sugg_qty} {sugg_uom}"
                }
                # You could also check if it's already in the recipe before appending
                st.session_state.recipe.append(new_row)

        elif action == "edit":
            # Find that row in st.session_state.recipe by id_entity
            for row in st.session_state.recipe:
                if row["id_entity"] == ent_id:
                    # Update the qty
                    row["qty"] = f"{sugg_qty} {sugg_uom}"
                    # Optionally update cost or name if needed
                    break

        elif action == "delete":
            # Remove from st.session_state.recipe by matching id_entity
            st.session_state.recipe = [
                row for row in st.session_state.recipe
                if row["id_entity"] != ent_id
            ]
        # else: ignore unknown actions

    # Once done, clear suggestions (if desired)
    st.session_state.agent_suggestions = []
    # Force a rerun so we see the updated table
    st.rerun()

from typing import Union
import pandas as pd
import re


def format_result(df: Union[pd.DataFrame, None]) -> str:
    if df is None or df.empty:
        return ""

    def get_comment(action):
        return {
            "APPROVED": "Approvato",
            "CHANGES_REQUESTED": "Richiesta una modifica",
            "COMMENTED": "Riguardato",
            "DISMISSED": "Rimossa l'apporvazione",
        }.get(action["review_state"], action["review_state"])

    def get_ticket(action):
        result = re.findall(r"([A-Z]{3,5}-\d+)", action["pull_request"])
        return "" if not result else result[0]

    def get_author(action):
        return action["assignee"]

    def action_to_string(action) -> str:
        action1 = action.to_dict()
        return f"{action['review_date']} {get_ticket(action1)} {get_comment(action1)} PR di @{get_author(action1)} {action1['url']}"

    lst = (
        df.groupby(by="number")
        .first()
        .reset_index()
        .apply(action_to_string, axis=1)
        .to_list()
    )

    lst.sort(reverse=True)
    return "\n".join(lst)

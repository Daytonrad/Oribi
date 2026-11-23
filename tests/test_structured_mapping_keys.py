import json

import pandas as pd
import pytest

from oribi import inspect


@pytest.mark.parametrize("export", ["to_dict", "to_json"])
@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("nested", [False, True])
def test_opt_in_structured_export_rejects_colliding_sample_keys(export, reverse, nested):
    entries = [(917, "numeric sample"), ("917", "text sample")]
    sample = dict(reversed(entries) if reverse else entries)
    if nested:
        sample = {"private parent key": [sample]}
    context = inspect(pd.DataFrame({"metadata": [sample]}))

    default = getattr(context, export)()
    if export == "to_json":
        default = json.loads(default)
    assert default["columns"][0]["statistics"]["top_values"] == []

    with pytest.raises(ValueError, match="duplicate stringified mapping key") as error:
        getattr(context, export)(include_values=True)
    message = str(error.value)
    assert "columns[0].statistics.top_values[0][0]" in message
    for private_text in ("917", "numeric sample", "text sample", "private parent key"):
        assert private_text not in message

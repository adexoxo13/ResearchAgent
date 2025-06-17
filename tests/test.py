import os
from tools import save_to_txt

def test_save_to_txt_creates_file(tmp_path):
    test_file = tmp_path / "test_output.txt"
    test_data = "Sample research output"
    save_to_txt(test_data, str(test_file))
    assert test_file.exists()
    content = test_file.read_text()
    assert "Sample research output" in content
from unittest.mock import patch

import pytest

from tilellm.tools.document_tools import _handle_trafilatura_scrape


URL = "https://example.org/dettagliostaff"
BANNER = "Cookie e privacy policy. " * 10
CONTENT = "Conteudo principal da pagina. " * 30


@pytest.mark.asyncio
async def test_short_precision_falls_back_to_default_extraction():
    def fake_extract(downloaded, **kwargs):
        return BANNER if kwargs.get("favor_precision") else CONTENT

    with patch("trafilatura.fetch_url", return_value="<html>page</html>"), \
            patch("trafilatura.extract", side_effect=fake_extract) as extract:
        docs = await _handle_trafilatura_scrape(URL)

    assert extract.call_count == 2
    assert docs[0].page_content == CONTENT.strip()


@pytest.mark.asyncio
async def test_long_precision_result_is_kept_without_retry():
    content = "Conteudo principal suficiente. " * 30

    with patch("trafilatura.fetch_url", return_value="<html>page</html>"), \
            patch("trafilatura.extract", return_value=content) as extract:
        docs = await _handle_trafilatura_scrape(URL)

    assert extract.call_count == 1
    assert docs[0].page_content == content.strip()


@pytest.mark.asyncio
async def test_both_extractions_short_returns_empty():
    with patch("trafilatura.fetch_url", return_value="<html>page</html>"), \
            patch("trafilatura.extract", return_value="curto"):
        docs = await _handle_trafilatura_scrape(URL)

    assert docs == []

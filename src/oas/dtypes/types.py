import typing as t
from lxml import etree # type: ignore

Article = t.Dict[str, t.Union[int, str, t.List[str]]]
Extractor = t.Callable[[etree.Element], t.Union[int, str, t.List[str]]]

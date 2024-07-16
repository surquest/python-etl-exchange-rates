from utils import misc

class TestEnum:

    def test__create_enum_class__basic(self):

        enum_list = ["a", "b", "c"]
        enum_class = misc.create_enum_class(enum_list=enum_list)
        assert enum_class.a.value == "a"
        assert enum_class.b.value == "b"
        assert enum_class.c.value == "c"
        assert enum_class.__class__.__name__ == "EnumType"

    def test__create_enum_class__named(self):
        enum_list = ["a", "b", "c"]
        enum_class = misc.create_enum_class(
            enum_list=enum_list,
            name="MyEnumClass"
        )
        assert enum_class.a.value == "a"
        assert enum_class.b.value == "b"
        assert enum_class.c.value == "c"
        assert enum_class.__name__ == "MyEnumClass"


class TestGetSubdirectories:


    def test__get_subdirectories__skip_hidden(self):

        path = "/opt/project"
        subdirectories = misc.get_subdirectories(path)

        for folder in ["config", "test", "src", "docs", "deploy"]:
            assert folder in subdirectories

    def test__get_subdirectories__include_hidden(self):

        path = "/opt/project"
        hidden_subdirectories = misc.get_subdirectories(path, skip_hidden=False)
        visible_subdirectories = misc.get_subdirectories(path, skip_hidden=True)

        assert len(hidden_subdirectories) >= len(visible_subdirectories)
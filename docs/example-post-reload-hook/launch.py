import hotload

class MathReloader(hotload.ReloadedPythonModule):
    def post_reload_hook(self, mod):
        mod.teststuff()
        mod.teststuff2()


hotload.hotload(
    watch=[
        hotload.listfiles(".", ext=".py")
    ],
    steps=[
        hotload.ClearTerminal(),
        MathReloader.from_module_name("mymath"),
    ]
)

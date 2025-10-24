import unreal

PATH = "/SpawnMan/Meshes/dance_hall_humanBody.dance_hall_humanBody"


def _get_first_selected_sma():
    # 권장: EditorActorSubsystem 사용
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_selected_level_actors():
        if isinstance(a, unreal.StaticMeshActor):
            return a
    return None


def _get_selected_asset():
    asset = unreal.EditorAssetLibrary.load_asset(PATH)
    return asset


def place_from_viewport(gap_cm: float = 2.0):
    base_actor = _get_first_selected_sma()
    if not base_actor:
        unreal.log_warning("No StaticMeshActor selected in the level.")
        return

    mesh_to_place = _get_selected_asset()
    if not mesh_to_place:
        unreal.log_warning(f"Asset not found: {PATH}")
        return

    # 선택 액터의 바운드 (월드 기준)
    origin, extent = base_actor.get_actor_bounds(False)  # (only_colliding_components=False)
    top_z = origin.z + extent.z

    # 스폰 위치: 선택 액터의 XY 중앙 + (상단 + 새 메시 반높이 + 갭)
    spawn_loc = unreal.Vector(origin.x, origin.y, top_z + gap_cm)

    spawn_rot = unreal.Rotator(0.0, 0.0, 0.0)

    # 액터 생성 및 메시 지정
    new_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor, spawn_loc, spawn_rot
    )
    if not new_actor:
        unreal.log_warning("Failed to spawn StaticMeshActor.")
        return

    smc = new_actor.static_mesh_component
    smc.set_static_mesh(mesh_to_place)
    smc.set_mobility(unreal.ComponentMobility.MOVABLE)

    # 혹시 미세 겹침이 있으면 살짝 위로 밀어올림(옵션)
    # new_actor.add_actor_world_offset(unreal.Vector(0, 0, 0.5), sweep=True)

    unreal.log(f"Spawned above '{base_actor.get_actor_label()}' at {spawn_loc}")


def _add_context_menu():
    menus = unreal.ToolMenus.get()

    my_menu = menus.extend_menu("LevelEditor.ActorContextMenu")
    section_name = f"SpwnMan"

    my_menu.add_section(section_name, "Spwn Man Tool")

    entry = unreal.ToolMenuEntry(
        name="SpwnMan.SpwnManCtx",
        type=unreal.MultiBlockType.MENU_ENTRY
    )
    entry.set_label("Spwn man")
    entry.set_string_command(
        type=unreal.ToolMenuStringCommandType.PYTHON,
        custom_type="",
        string="place_from_viewport()"
    )
    my_menu.add_menu_entry(section_name, entry)

    menus.refresh_all_widgets()


# 에디터 시작 시 한 번 등록
_add_context_menu()
unreal.log("StaticMeshActor initialized")

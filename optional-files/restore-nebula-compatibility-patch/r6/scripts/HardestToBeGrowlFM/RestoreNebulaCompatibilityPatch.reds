// ======================================================================================
// Mod Name: Hardest to Be on Growl FM - Restore Nebula Compatibility Patch
// File: RestoreNebulaCompatibilityPatch.reds
// Author: Spuddeh
// Description: Puts Restore Nebula's track on Growl FM when a mod that reads the station data at
//              script start is installed. Restore Nebula adds its track only when it hears that
//              data finish loading, and a resource another mod has already asked for is not
//              announced again, so beside Native Radio Framework or Hardest to Be the track is
//              never added. This reads each resource directly and adds the row itself, with a
//              check first, so it adds nothing twice and does nothing when Restore Nebula is not
//              installed. The audio, the title and everything else stay Restore Nebula's.
// File Version: 1.0.0
// Credits: arman3 (Restore Nebula), psiberx (Codeware), DigitalVixen (RedLogger)
// ======================================================================================

module HardestToBeGrowlFM.RestoreNebulaCompatibilityPatch

@if(ModuleExists("RedLogger"))
import RedLogger.*

@if(ModuleExists("RedLogger"))
public func RestoreNebulaPatchLog(msg: String) -> Void {
  RedLog.Append("HardestToBeGrowlFM", msg);
}

@if(!ModuleExists("RedLogger"))
public func RestoreNebulaPatchLog(msg: String) -> Void {}

public class HardestToBeRestoreNebulaPatch extends ScriptableService {

  // The values Restore Nebula 1.04 writes. Facts about its archive, not its code: the event the
  // bank defines, that event's Wwise id and length, and the title's two keys.
  private let m_event: CName = n"mus_radio_12_nebula_new";
  private let m_wwiseId: Uint32 = 2159894381u;
  private let m_duration: Float = 178.0;
  private let m_station: CName = n"radio_station_12_growl_fm";
  private let m_locName: CName = n"Gameplay-Devices-Radio_tracks-growl_nebula";
  private let m_locKey: Uint64 = 93687ul;

  private let m_tokens: array<ref<ResourceToken>>;

  private cb func OnLoad() {
    let depot = GameInstance.GetResourceDepot();
    // A file only Restore Nebula's archive provides. Without it there is no audio to point at,
    // and adding the row would put silence on the station.
    if !depot.ResourceExists(r"mod\\arman3_return_nebula\\localization\\en-us\\onscreens\\restore_nebula_onscreens.json") {
      RestoreNebulaPatchLog("Restore Nebula is not installed - compatibility patch idle");
      return;
    }

    let cb = GameInstance.GetCallbackSystem();
    cb.RegisterCallback(n"Resource/Load", this, n"OnEventsMetadata")
      .AddTarget(ResourceTarget.Path(r"base\\sound\\event\\eventsmetadata.json"));
    cb.RegisterCallback(n"Resource/Load", this, n"OnCookedMetadata")
      .AddTarget(ResourceTarget.Path(r"base\\sound\\metadata\\cooked_metadata.audio_metadata"));

    this.Watch(depot, r"base\\sound\\event\\eventsmetadata.json", n"OnEventsReady");
    this.Watch(depot, r"base\\sound\\metadata\\cooked_metadata.audio_metadata", n"OnCookedReady");
  }

  private func Watch(depot: ref<ResourceDepot>, path: ResRef, callback: CName) -> Void {
    let token = depot.LoadResource(path);
    if IsDefined(token) {
      ArrayPush(this.m_tokens, token);
      token.RegisterCallback(this, callback);
    }
  }

  private cb func OnEventsMetadata(event: ref<ResourceEvent>) {
    this.AddEvent(event.GetResource() as JsonResource);
  }

  private cb func OnEventsReady(token: ref<ResourceToken>) {
    this.AddEvent(token.GetResource() as JsonResource);
  }

  private cb func OnCookedMetadata(event: ref<ResourceEvent>) {
    this.AddTrack(event.GetResource() as audioCookedMetadataResource);
  }

  private cb func OnCookedReady(token: ref<ResourceToken>) {
    this.AddTrack(token.GetResource() as audioCookedMetadataResource);
  }

  // The event row: name to Wwise id, and the length the station schedules on.
  private func AddEvent(json: ref<JsonResource>) -> Void {
    if !IsDefined(json) { return; }
    let events = json.root as audioAudioEventArray;
    if !IsDefined(events) { return; }
    let i: Int32 = 0;
    while i < ArraySize(events.events) {
      if Equals(events.events[i].redId, this.m_event) { return; }
      i += 1;
    }
    let row: audioAudioEventMetadataArrayElement;
    row.redId = this.m_event;
    row.wwiseId = this.m_wwiseId;
    row.maxDuration = this.m_duration;
    row.minDuration = this.m_duration;
    row.isLooping = false;
    row.maxAttenuation = 0;
    row.tags = [n"GrowlFM"];
    ArrayPush(events.events, row);
    RestoreNebulaPatchLog("Nebula: event row added as the event table loaded");
  }

  // The station's track list and the title table.
  private func AddTrack(cooked: ref<audioCookedMetadataResource>) -> Void {
    if !IsDefined(cooked) { return; }
    let added: Bool = false;
    for entry in cooked.entries {
      let station = entry as audioRadioStationMetadata;
      if IsDefined(station) && Equals(station.name, this.m_station) && !ArrayContains(station.tracks, this.m_event) {
        ArrayPush(station.tracks, this.m_event);
        added = true;
      }
      let titles = entry as audioRadioTracksMetadata;
      if IsDefined(titles) && !this.HasTitle(titles) {
        let row: audioRadioTrack;
        row.trackEventName = this.m_event;
        row.localizationKey = this.m_locName;
        row.primaryLocKey = this.m_locKey;
        row.isStreamingFriendly = true;
        ArrayPush(titles.radioTracks, row);
      }
    }
    if added {
      RestoreNebulaPatchLog("Nebula: track added to Growl FM as the station data loaded");
    }
  }

  private func HasTitle(titles: ref<audioRadioTracksMetadata>) -> Bool {
    let i: Int32 = 0;
    while i < ArraySize(titles.radioTracks) {
      if Equals(titles.radioTracks[i].trackEventName, this.m_event) { return true; }
      i += 1;
    }
    return false;
  }
}

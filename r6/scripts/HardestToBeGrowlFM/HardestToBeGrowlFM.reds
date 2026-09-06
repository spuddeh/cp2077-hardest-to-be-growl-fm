// ======================================================================================
// Mod Name: Hardest to Be on Growl FM
// Author: Spuddeh
// Description: Adds the Alex heart-to-heart jukebox song to Growl FM's playlist.
// File Version: 0.1.0
// Credits: Restore Nebula by ArmanIII, for the runtime metadata patch; AudioXL by DigitalVixen.
// ======================================================================================

module HardestToBeGrowlFM

// RedLogger's signature ships once, inside the plugin, so callers cannot collide. Without
// RedLogger installed this compiles to nothing.
@if(ModuleExists("RedLogger"))
import RedLogger.*

@if(ModuleExists("RedLogger"))
public func HardestLog(msg: String) -> Void {
  RedLog.Append("HardestToBeGrowlFM", msg);
}

@if(!ModuleExists("RedLogger"))
public func HardestLog(msg: String) -> Void {}

// A radio playlist is not TweakDB. The station record holds only its name, icon and index; the
// track list lives in two cooked resources, and both are patched here as they load:
//
//   eventsmetadata.json          name -> Wwise id, and the duration the station schedules against
//   cooked_metadata.audio_metadata   the audioRadioTrack rows and each station's track array
//
// The Wwise event itself comes from hardest_to_be_growl.bnk, which AudioXL loads.

public class HardestToBeGrowlFM extends ScriptableService {

  // Matches the event built by tools/make_bank.py. Change one, change the other.
  private let m_trackEvent: CName = n"mus_radio_12_hardest_to_be";
  private let m_wwiseId: Uint32 = 706539828u;

  // The source file runs 206897.3958 ms. The station uses this to know when to queue the next
  // track, so it must match the segment length in the bank.
  private let m_duration: Float = 206.8974;

  private let m_station: CName = n"radio_station_12_growl_fm";

  // Placeholder title, taken from the credits. A properly formatted string needs its own LocKey.
  private let m_locName: CName = n"UI-Credits-HARDEST_TO_BE";
  private let m_locKey: Uint64 = 94636ul;

  private cb func OnLoad() {
    GameInstance
      .GetCallbackSystem()
      .RegisterCallback(n"Resource/Loaded", this, n"OnEventsMetadata")
      .AddTarget(ResourceTarget.Path(r"base\\sound\\event\\eventsmetadata.json"));

    GameInstance
      .GetCallbackSystem()
      .RegisterCallback(n"Resource/Loaded", this, n"OnCookedMetadata")
      .AddTarget(
        ResourceTarget.Path(r"base\\sound\\metadata\\cooked_metadata.audio_metadata")
      );
  }

  private cb func OnEventsMetadata(event: ref<ResourceEvent>) {
    let resource = event.GetResource() as JsonResource;
    if !IsDefined(resource) { return; }

    let events = resource.root as audioAudioEventArray;
    if !IsDefined(events) { return; }

    let i: Int32 = 0;
    while i < ArraySize(events.events) {
      if Equals(events.events[i].redId, this.m_trackEvent) { return; }
      i += 1;
    }

    let row: audioAudioEventMetadataArrayElement;
    row.redId = this.m_trackEvent;
    row.wwiseId = this.m_wwiseId;
    row.isLooping = false;
    row.maxAttenuation = 0.0;
    row.minDuration = this.m_duration;
    row.maxDuration = this.m_duration;
    row.tags = [n"GrowlFM"];
    ArrayPush(events.events, row);
    HardestLog(s"event registered: \(this.m_trackEvent) wwiseId \(this.m_wwiseId) \(this.m_duration)s");
  }

  private cb func OnCookedMetadata(event: ref<ResourceEvent>) {
    let cooked = event.GetResource() as audioCookedMetadataResource;
    if !IsDefined(cooked) { return; }

    let station: Bool = false;
    let tracks: Bool = false;

    for entry in cooked.entries {
      let stationData = entry as audioRadioStationMetadata;
      if IsDefined(stationData) && Equals(stationData.name, this.m_station) {
        if !ArrayContains(stationData.tracks, this.m_trackEvent) {
          ArrayPush(stationData.tracks, this.m_trackEvent);
        }
        HardestLog(s"\(this.m_station) now lists \(ArraySize(stationData.tracks)) tracks");
        station = true;
      }

      let trackData = entry as audioRadioTracksMetadata;
      if IsDefined(trackData) && !this.HasTrack(trackData) {
        let row: audioRadioTrack;
        row.trackEventName = this.m_trackEvent;
        row.localizationKey = this.m_locName;
        row.primaryLocKey = this.m_locKey;
        row.isStreamingFriendly = true;
        ArrayPush(trackData.radioTracks, row);
        tracks = true;
      }

      if station && tracks { break; }
    }
  }

  private func HasTrack(trackData: ref<audioRadioTracksMetadata>) -> Bool {
    let i: Int32 = 0;
    while i < ArraySize(trackData.radioTracks) {
      if Equals(trackData.radioTracks[i].trackEventName, this.m_trackEvent) { return true; }
      i += 1;
    }
    return false;
  }
}

import { Component, NgZone, OnInit } from '@angular/core';
import * as OpenSeadragon from 'openseadragon';



@Component({
  selector: 'app-slide-viewer',
  templateUrl: './slide-viewer.component.html',
  styleUrls: ['./slide-viewer.component.scss'],
})
export class SlideViewerComponent implements OnInit {
  viewer: any;
  slideData: any;
  constructor(private ngZone:NgZone){}
  ngOnInit() {
    let slideName = "slide_1.svs";
    this.initOpenSeadragon(slideName);
  }

  async initOpenSeadragon(slideName: string) {
    try {
      let response = await fetch(`http://127.0.0.1:5000/slide/metadata/${slideName}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      this.slideData = await response.json();
      this.initViewer(slideName);
    } catch (error) {
      console.error("Failed to fetch slide metadata:", error);
      // Handle the error appropriately
    }
  }

  private initViewer(slideName: string) {
    this.viewer = this.ngZone.runOutsideAngular(() =>
      OpenSeadragon({
          id: 'openseadragon-viewer',
          prefixUrl: '//openseadragon.github.io/openseadragon/images/',
          tileSources: {
            height: this.slideData.dimensions[0],
            width: this.slideData.dimensions[1],
            overlap: this.slideData.overlap,
            tileSize: this.slideData.tile_size,
            getTileUrl: function (level: number, x: number, y: number) {
              return `http://127.0.0.1:5000/slide/${slideName}/${level}/${x}_${y}.jpeg`;
            },
          },
          showNavigator: true,
          showRotationControl: true,
          timeout: 100000,
        })
    );
  }
}

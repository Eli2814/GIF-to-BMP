#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "____________"         // your generated header

// OLED display configuration
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
#define OLED_RESET    -1      // not used
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// How long each frame shows (ms)
const uint16_t FRAME_DELAY = 200;

// Tracks which frame we’re on
uint8_t currentFrame = 0;
unsigned long lastFrameTime = 0;

void setup() {
  // Start I2C and OLED
  Wire.begin();
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    // OLED didn’t respond
    for (;;);
  }
  display.clearDisplay();
}

void loop() {
  unsigned long now = millis();
  if (now - lastFrameTime < FRAME_DELAY) return;  // not time yet

  lastFrameTime = now;

  // Pull pointer out of flash (PROGMEM)
  const uint8_t* framePtr = 
     (const uint8_t*)pgm_read_ptr(&frameList[currentFrame]);

  display.clearDisplay();
  // Draw the bitmap at 0,0. If your frames are smaller, center them:
  // int x = (SCREEN_WIDTH  - FRAME_WIDTH ) / 2;
  // int y = (SCREEN_HEIGHT - FRAME_HEIGHT) / 2;
  display.drawBitmap(0, 0, framePtr, SCREEN_WIDTH, SCREEN_HEIGHT, SSD1306_WHITE);
  display.display();

  // Advance frame (looping)
  currentFrame++;
  if (currentFrame >= frameCount) currentFrame = 0;
}

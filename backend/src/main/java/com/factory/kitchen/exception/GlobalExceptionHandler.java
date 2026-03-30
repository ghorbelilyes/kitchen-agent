package com.factory.kitchen.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.multipart.MaxUploadSizeExceededException;

import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(MaxUploadSizeExceededException.class)
    public ResponseEntity<Map<String, Object>> handleMaxUploadSizeExceeded(MaxUploadSizeExceededException e) {
        return ResponseEntity.status(HttpStatus.PAYLOAD_TOO_LARGE)
            .body(Map.of(
                "success", false,
                "error", "FILE_TOO_LARGE",
                "message", "Kitchen plan image exceeds the maximum allowed size (e.g. 20MB)."
            ));
    }

    // TODO: Add handlers for InvalidImageFormatException, ValidationEngineException, etc.
}

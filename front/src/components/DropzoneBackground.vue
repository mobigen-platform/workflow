<template>
  <div class="dropzone-background">
    <Background :size="2" :gap="20" pattern-color="#BDBDBD"/>

    <div class="overlay">
      <slot/>
    </div>
  </div>
</template>

<script setup>
import {Background} from '@vue-flow/core'
</script>

<style>
@import "@/scripts/editer.css";
</style>

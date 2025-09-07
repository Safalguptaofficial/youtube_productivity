#!/usr/bin/env node

// Quick storage test
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY;
const bucketName = process.env.SUPABASE_BUCKET;

const supabase = createClient(supabaseUrl, supabaseKey);

async function testStorage() {
  console.log('🧪 Testing Storage Access...');
  console.log(`📍 Bucket: ${bucketName}`);
  console.log('');

  try {
    // Test 1: List buckets
    const { data: buckets, error: listError } = await supabase.storage.listBuckets();
    
    if (listError) {
      console.error('❌ Error listing buckets:', listError.message);
      return;
    }
    
    const bucket = buckets.find(b => b.name === bucketName);
    if (!bucket) {
      console.error(`❌ Bucket '${bucketName}' not found`);
      return;
    }
    
    console.log(`✅ Bucket found: ${bucket.name} (public: ${bucket.public})`);
    console.log('');

    // Test 2: Upload a test file
    console.log('📤 Testing file upload...');
    const testContent = 'Hello YouTube Productivity!';
    const testFileName = `test-${Date.now()}.txt`;
    
    const { data: uploadData, error: uploadError } = await supabase.storage
      .from(bucketName)
      .upload(testFileName, testContent, {
        contentType: 'text/plain'
      });
    
    if (uploadError) {
      console.error('❌ Upload failed:', uploadError.message);
      return;
    }
    
    console.log('✅ Upload successful!');
    console.log(`   File: ${uploadData.path}`);
    console.log('');

    // Test 3: Get public URL
    const { data: publicUrlData } = supabase.storage
      .from(bucketName)
      .getPublicUrl(testFileName);
    
    console.log('🔗 Public URL:');
    console.log(`   ${publicUrlData.publicUrl}`);
    console.log('');

    // Test 4: Download the file
    console.log('📥 Testing file download...');
    const { data: downloadData, error: downloadError } = await supabase.storage
      .from(bucketName)
      .download(testFileName);
    
    if (downloadError) {
      console.error('❌ Download failed:', downloadError.message);
    } else {
      const content = await downloadData.text();
      console.log('✅ Download successful!');
      console.log(`   Content: "${content}"`);
    }
    console.log('');

    // Test 5: Clean up
    console.log('🧹 Cleaning up test file...');
    const { error: deleteError } = await supabase.storage
      .from(bucketName)
      .remove([testFileName]);
    
    if (deleteError) {
      console.error('❌ Delete failed:', deleteError.message);
    } else {
      console.log('✅ Test file cleaned up');
    }

    console.log('');
    console.log('🎉 Storage test completed successfully!');
    console.log('🚀 Your Supabase setup is fully ready!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

testStorage();

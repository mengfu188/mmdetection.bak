# model settings
model = dict(
    type='RetinaNet',
    pretrained='torchvision://mobilenet_v2',
    backbone=dict(
        type='MobileNetV2',
        out_indices=(3, 6, 13, 18)),
    neck=dict(
        type='FPN',
        in_channels=[24, 32, 96, 1280],
        out_channels=64,
        num_outs=5),
    bbox_head=dict(
        type='RetinaHead',
        num_classes=3,
        in_channels=64,
        stacked_convs=4,
        feat_channels=64,
        octave_base_scale=4,
        scales_per_octave=3,
        anchor_ratios=[1.0],
        anchor_strides=[8, 16, 32, 64, 128],
        target_means=[.0, .0, .0, .0],
        target_stds=[1.0, 1.0, 1.0, 1.0],
        loss_cls=dict(
            type='FocalLoss',
            use_sigmoid=True,
            gamma=2.0,
            alpha=0.25,
            loss_weight=1.0),
        loss_bbox=dict(type='SmoothL1Loss', beta=0.11, loss_weight=1.0)))
# training and testing settings
train_cfg = dict(
    assigner=dict(
        type='MaxIoUAssigner',
        pos_iou_thr=0.5,
        neg_iou_thr=0.4,
        min_pos_iou=0,
        ignore_iof_thr=-1),
    allowed_border=-1,
    pos_weight=-1,
    debug=False)
test_cfg = dict(
    nms_pre=1000,
    min_bbox_size=0,
    score_thr=0.05,
    nms=dict(type='nms', iou_thr=0.5),
    max_per_img=100)

img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations', with_bbox=True),
    dict(type='Resize', img_scale=(1333, 800), keep_ratio=True),
    dict(type='RandomFlip', flip_ratio=0.5),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='Pad', size_divisor=32),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_bboxes', 'gt_labels']),
]
test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=(1333, 800),
        flip=False,
        transforms=[
            dict(type='Resize', keep_ratio=True),
            dict(type='RandomFlip'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='Pad', size_divisor=32),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img']),
        ])
]
# dataset settings
dataset_type = 'HelmetMergeDataset'
data_root = '/datasets/HelmetMerge/'

data = dict(
    imgs_per_gpu=4,
    workers_per_gpu=4,
    train=dict(type=dataset_type,
        data_root=data_root,
        ann_file=data_root + 'ImageSets/Main/trainval.txt',
        img_prefix=data_root,
        pipeline=train_pipeline,
        use_ignore=True),
    val=dict(
        type=dataset_type,
        data_root=data_root,
        ann_file=data_root + 'ImageSets/Main/test.txt',
        img_prefix=data_root,
        pipeline=test_pipeline),
    test=dict(
        type=dataset_type,
        data_root=data_root,
        ann_file=data_root + 'ImageSets/Main/test.txt',
        img_prefix=data_root,
        pipeline=test_pipeline),)
# optimizer
optimizer = dict(type='SGD', lr=0.005, momentum=0.9, weight_decay=0.0001)
optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))
# learning policy
lr_config = dict(
    policy='step',
    warmup='linear',
    warmup_iters=500,
    warmup_ratio=1.0 / 3,
    step=[8, 11])
checkpoint_config = dict(interval=1)
# yapf:disable
log_config = dict(
    interval=50,
    hooks=[
        dict(type='TextLoggerHook'),
        dict(type='TensorboardLoggerHook')
    ])
# yapf:enable
# runtime settings
total_epochs = 12
dist_params = dict(backend='nccl')
log_level = 'INFO'
work_dir = __file__.replace('configs', 'work_dirs').rstrip('.py')
load_from = None
resume_from = None
workflow = [('train', 1)]
